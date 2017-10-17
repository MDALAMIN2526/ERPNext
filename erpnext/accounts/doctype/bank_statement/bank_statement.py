# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, csv, datetime, os, re
from frappe import _
from frappe.utils import flt, date_diff, getdate, dateutils, get_datetime
from frappe.model.document import Document
from frappe.utils.file_manager import get_file_path, get_uploaded_content

# just for reference, no longer used
dateformats = {
	'1990-01-31': '%Y-%m-%d',
	'31-01-1990': '%d-%m-%Y',
	'31/01/1990': '%d/%m/%Y',
	'31.01.1990': '%d.%m.%Y',
	'01/31/1990': '%m/%d/%Y',
	'01-31-1990': '%m-%d-%Y',
	'1990-JAN-31': '%Y-%b-%d',
	'31-JAN-1990': '%d-%b-%Y',
	'31/JAN/1990': '%d/%b/%Y',
	'31.JAN.1990': '%d.%b.%Y',
	'JAN/31/1990': '%b/%d/%Y',
	'JAN-31-1990': '%b-%d-%Y',
}

class BankStatement(Document):

	def validate(self):
		self.validate_dates()
		if not self.previous_bank_statement: self.fill_previous_statement()

	def validate_dates(self):
		previous_sta = frappe.get_all("Bank Statement", fields=['statement_end_date','bank','account_no', 'name'],
						filters={'name': ['!=', getattr(self,'name',"")], 'creation': ['<', getattr(self,'creation',get_datetime())]})
		end_dates = [(s.name,s.statement_end_date) for s in previous_sta if (s.bank == self.bank \
			and s.account_no == self.account_no and s.statement_end_date >= getdate(self.statement_start_date))]
		end_dates = filter(lambda x: isinstance(x[1], datetime.date), end_dates)
		if end_dates:
			previous_statement_end_date = sorted(end_dates, key=lambda x:x[1], reverse=True)[0]
			if getdate(self.statement_start_date) > getdate(self.statement_end_date):
				frappe.throw(_("Statement start date cannot be later than end date"))
			if getdate(self.statement_start_date) <= previous_statement_end_date[1]:
				prev_doc_name = previous_statement_end_date[0]
				frappe.throw(_("Statement start date cannot be same as or earlier than a previous statement's end date ({})".format(prev_doc_name)))

	def check_end_date(self):
		previous_sta = frappe.get_all("Bank Statement", fields=['statement_start_date','bank','account_no'])
		end_dates = [s.statement_start_date for s in previous_sta if (s.bank == self.bank and s.account_no == self.account_no)]
		for e_date in end_dates:
			date_interval = date_diff(self.statement_start_date, e_date)
			if date_interval > 1:      # if start date is greater than an end date by a day
				return {'gap': date_interval}
		return {'gap': False}

	def fill_previous_statement(self):
		previous_sta = []
		all_previous_sta = frappe.get_all("Bank Statement", fields=['statement_end_date','bank','account_no', 'name'],
							filters={'name': ['!=', getattr(self,'name',"")]}, order_by='creation')
		for sta in all_previous_sta:
			if (sta.bank == self.bank) and (sta.account_no == self.account_no) and (getdate(self.statement_start_date) >= sta.statement_end_date):
				previous_sta.append(sta)
		if not previous_sta: return

		if len(previous_sta) > 1:
			previous_sta.sort(key=lambda x: x.statement_end_date, reverse=True)

		self.previous_bank_statement = previous_sta[0].name

	def check_file_format(self, csv_header_list):
		sta_format = frappe.get_doc("Bank Statement Format",self.bank_statement_format)
		source_fields = set(s.source_field for s in sta_format.bank_statement_mapping_item)
		if not (set(csv_header_list) >= source_fields):
			frappe.msgprint(_("The attached statement does not contain all the columns specified in the format selected"))

	def convert_to_internal_format(self, csv_column_header, csv_row_field_value, bank_statement_mapping_items, eval_data):
		# select mapping_row from bank_statement_mapping_item where source_field = csv_column_header
		mapping_row = None
		for row in bank_statement_mapping_items:
			if row.source_field == csv_column_header:
				mapping_row = row
		if not mapping_row: return

		if not (mapping_row.source_field_abbr or mapping_row.transformation_rule):
			return mapping_row.target_field, csv_row_field_value
		transformation_rule = mapping_row.source_field_abbr.strip() if not mapping_row.transformation_rule else mapping_row.transformation_rule.strip()
		csv_row_field_value = self.eval_transformation(transformation_rule, mapping_row.source_field_abbr.strip(), eval_data)
		eval_data[mapping_row.target_field_abbr.strip()] = csv_row_field_value

		return mapping_row.target_field, csv_row_field_value

	def fill_table(self):
		if not self.file: return
		file_doc = frappe._dict()
		self.bank_statement_items = []
		bank_statement_mapping_items = frappe.get_doc("Bank Statement Format", self.bank_statement_format).bank_statement_mapping_item
		file_id = frappe.db.sql("""SELECT name FROM tabFile WHERE attached_to_doctype = '{0}' AND attached_to_name = '{1}'
						""".format("Bank Statement", self.name), as_dict=1)
		file_doc = frappe.get_doc("File",file_id[0].name)
		filename, file_extension = os.path.splitext(self.file)

		if file_extension == '.xlsx':
			from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file
			rows = read_xlsx_file_from_attached_file(file_id=file_doc.name)
		elif file_extension == '.csv':
			from frappe.utils.file_manager import get_file
			from frappe.utils.csvutils import read_csv_content
			fname, fcontent = get_file(file_doc.name)
			rows = read_csv_content(fcontent)
		else:
			frappe.throw(_("Unsupported File Format"))

		csv_header_list = rows[0]
		data_rows = rows[1:]

		self.check_file_format(csv_header_list)

		intermediate_bank_statement_items = []
		# create a list of maps, intermediate_bank_statement_items, to hold bank statement items based on internal > 
		# < representation see "Bank Statement Item" definition
		for statement_row in data_rows:
			bank_sta_item = dict()
			eval_data = self.get_data_for_eval(statement_row, csv_header_list, bank_statement_mapping_items)
			for column_index, column_value in enumerate(statement_row):
				column_value = str(column_value) if column_value else None
				itm = self.convert_to_internal_format(csv_header_list[column_index], column_value, bank_statement_mapping_items, eval_data)
				if not itm: continue
				target_field, eval_result = itm
				bank_sta_item[frappe.scrub(target_field)] = eval_result
			intermediate_bank_statement_items.append(bank_sta_item) if bank_sta_item else None

		for idx, sta in enumerate(intermediate_bank_statement_items):
			sta['transaction_type'] = processs_statement(self, idx+1, sta)
			self.append('bank_statement_items', sta)  # create bank_statement_item table entries

		self.save()

	def eval_transformation(self, eval_code, source_abbr, eval_data):
		if not eval_code:
			frappe.msgprint(_("There is no eval code"))
			return
		try:
			eval_result = frappe.safe_eval(eval_code, None, eval_data)
			return eval_result

		except NameError as err:
			frappe.throw(_("Name error: {0}".format(err)))
		except SyntaxError as err:
			frappe.throw(_("Syntax error in formula or condition: {0}".format(err)))
		except Exception as e:
			frappe.throw(_("Error in formula or condition: {0}".format(e)))
			raise

	def get_data_for_eval(self, statement_row, csv_header_list, bank_statement_mapping_items):
		'''Returns data object for evaluating formula'''
		data = frappe._dict()
		for column_index, column_value in enumerate(statement_row):
			source_abbr = get_source_abbr(csv_header_list[column_index], bank_statement_mapping_items)
			if not source_abbr: continue
			data[source_abbr] = str(column_value) if column_value else None
			
		data["reformat_date"] = reformat_date
		return data

	def get_account_no(self):
		bank = frappe.get_doc("Bank", self.bank)
		ret_dict = {
			'acc_nos': [acc.account_number for acc in bank.bank_accounts],
			'currency_map': {acc.account_number:acc.currency for acc in bank.bank_accounts}
		}
		return ret_dict

	def process_statement(self):
		'''To be removed. Matching of transaction type to be done on statement upload'''
		if not self.bank_statement_items: return
		txn_type_derivation = frappe.db.get_value("Bank Statement Format", self.bank_statement_format, 'txn_type_derivation')
		if not txn_type_derivation == "Derive Using Bank Transaction Type": return
		ret_list = []
		for idx, itm in enumerate(self.bank_statement_items):
			match_type = []
			if itm.credit_amount:
				DR_or_CR = 'CR'
			elif itm.debit_amount:
				DR_or_CR = 'DR'
			else:
				DR_or_CR = None
			bnks_txn_types = frappe.get_all('Bank Transaction Type',
									filters={'bank_statement_format': self.bank_statement_format, 'debit_or_credit': DR_or_CR},
									fields=['name', 'transaction_type_match_expression', 'ignore_case', 'multi_line', 'dot_all'])
			for txn_type in bnks_txn_types:
				re_flag = 0
				for i,d in [('ignore_case', re.I), ('dot_all', re.S), ('multi_line', re.M)]:
					if txn_type.get(i): re_flag = re_flag | d
				txn_match = re.search(txn_type.transaction_type_match_expression, itm.transaction_description, flags=re_flag)
				if txn_match:
					match_type.append(txn_type)
			# @innocent in the check below, we need to set the status of the bank statement item to show that either no item was found or more than one item was found
			if len(match_type) != 1:
				ret_list.append({'row': idx+1, 'matches': match_type})
				continue
			itm.transaction_type = match_type[0].name
		get_ret_msg(ret_list)
		self.save()

def get_source_abbr(source_field, bank_statement_mapping_items):
	for row in bank_statement_mapping_items:
		if row.source_field == source_field:
			return row.source_field_abbr
	
def reformat_date(date_string, from_format):
	if date_string and from_format:
		return datetime.datetime.strptime(date_string, from_format).strftime('%Y-%m-%d')

def get_ret_msg(ret_list):
	if not ret_list: return
	for i in ret_list:
		if len(i.get('matches')) == 0:
			frappe.msgprint('No match was found for item in row {} \n'.format(i.get('row')))
			continue
		ret_msg = ''
		ret_msg += 'Multiple matches were found for item in row {} \n'.format(i.get('row'))
		for match in i.get('matches'):
			ret_msg += '<ul> {} </ul>'.format(match.get('name'))
		frappe.msgprint(ret_msg)


def processs_statement(self, idx, itm):
	itm = frappe._dict(itm)
	ret_list = []
	txn_type_derivation = frappe.db.get_value("Bank Statement Format", self.bank_statement_format, 'txn_type_derivation')
	if not txn_type_derivation == "Derive Using Bank Transaction Type": return
	match_type = []
	if itm.credit_amount:
		DR_or_CR = 'CR'
	elif itm.debit_amount:
		DR_or_CR = 'DR'
	else:
		DR_or_CR = None
	bnks_txn_types = frappe.get_all('Bank Transaction Type',
							filters={'bank_statement_format': self.bank_statement_format, 'debit_or_credit': DR_or_CR},
							fields=['name', 'transaction_type_match_expression', 'ignore_case', 'multi_line', 'dot_all'])
	for txn_type in bnks_txn_types:
		re_flag = 0
		for i,d in [('ignore_case', re.I), ('dot_all', re.S), ('multi_line', re.M)]:
			if txn_type.get(i): re_flag = re_flag | d
		txn_match = re.search(txn_type.transaction_type_match_expression, itm.transaction_description, flags=re_flag)
		if txn_match:
			match_type.append(txn_type)
	# @innocent in the check below, we need to set the status of the bank statement item to show that either no item was found or more than one item was found
	if len(match_type) != 1:
		ret_list.append({'row': idx, 'matches': match_type})
		get_ret_msg(ret_list)
		return
	return match_type[0].name
