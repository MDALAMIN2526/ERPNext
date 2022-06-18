# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	if not filters: filters = {}
	columns = [
		{
   			"fieldname": "transaction",
  			"fieldtype": "Data",
  			"label": "Transaction",
  		},
		{
   			"fieldname": "date",
  			"fieldtype": "Data",
  			"label": "Date",
  		},
		{
			"fieldname": "document_number",
   			"fieldtype": "Link",
   			"label": "Document Number",
			"options": "Bank Transactions"
		},
		{
   			"fieldname": "party",
  			"fieldtype": "Data",
  			"label": "Party",
  		},
		{
   			"fieldname": "debits",
  			"fieldtype": "Currency",
  			"label": "Debits",
  		},
		{
   			"fieldname": "credits",
  			"fieldtype": "Currency",
  			"label": "Credits",
  		},
		{
   			"fieldname": "qty",
  			"fieldtype": "data",
  			"label": "Quantity",
  		}
	]
	data = []

	if filters.get("from_date"): from_date = filters.get("from_date")
	if filters.get("to_date"): to_date = filters.get("to_date")

	##Bank Deposit
	conditions_deposit = get_conditions_deposit(filters, from_date, to_date)

	deposits = frappe.get_all("Bank Transactions", ["*"], filters = conditions_deposit)
	
	total_deposit = 0

	registers = []

	for deposit in deposits:
		total_deposit += deposit.amount_bd
		product_arr = {'indent': 1.0,  "date": deposit.deposit_date, "document_number": deposit.name, "party": deposit.person_name, "credits": deposit.amount_bd, "qty":1}
		registers.append(product_arr)

	group_arr = [{'indent': 0.0, "transaction": "Deposito Bancario", "credits": total_deposit, "qty":len(deposits)}]
	data.extend(group_arr or [])
	data.extend(registers or [])

	##Credit Note
	conditions_credit_note = get_conditions_credit_note(filters, from_date, to_date)

	credits = frappe.get_all("Bank Transactions", ["*"], filters = conditions_credit_note)
	
	total_credits = 0
	registers = []

	for credit in credits:
		total_credits += credit.amount_nc
		product_arr = {'indent': 1.0,  "date": credit.check_date_nc, "document_number": credit.name, "party": credit.person_name, "credits": credit.amount_nc, "qty":1}
		registers.append(product_arr)

	group_arr = [{'indent': 0.0, "transaction": "Nota de Credito", "credits": total_credits, "qty":len(credits)}]
	data.extend(group_arr or [])
	data.extend(registers or [])

	##Debit Note
	conditions_debit_note = get_conditions_debit_note(filters, from_date, to_date)

	debits = frappe.get_all("Bank Transactions", ["*"], filters = conditions_debit_note)
	
	total_debits = 0
	registers = []

	for debit in debits:
		total_debits += debit.amount_nd
		product_arr = {'indent': 1.0,  "date": debit.check_date_nd, "document_number": debit.name, "party": debit.person_name, "debits": debit.amount_nd, "qty":1}
		registers.append(product_arr)

	group_arr = [{'indent': 0.0, "transaction": "Nota de Debito", "debits": total_debits, "qty":len(debits)}]
	data.extend(group_arr or [])
	data.extend(registers or [])

	##Bank Check
	conditions_check = get_conditions_check(filters, from_date, to_date)

	checks = frappe.get_all("Bank Transactions", ["*"], filters = conditions_check)
	
	total_checks = 0
	registers = []
	
	for check in checks:
		total_checks += check.amount
		product_arr = {'indent': 1.0,  "date": check.check_date, "document_number": check.name, "party": check.person_name, "debits": check.amount, "qty":1}
		registers.append(product_arr)

	group_arr = [{'indent': 0.0, "transaction": "Cheques Bancarios", "debits": total_checks, "qty":len(checks)}]
	data.extend(group_arr or [])
	data.extend(registers or [])

	debits_totals = total_debits + total_checks
	credits_totals = total_deposit + total_credits
	qty_totals = len(debits) + len(checks) + len(credits) + len(deposits)
	group_arr = [{'indent': 0.0, "transaction": "Total", "debits": debits_totals, "credits": credits_totals, "qty":qty_totals}]
	data.extend(group_arr or [])

	return columns, data

def get_conditions_deposit(filters, from_date, to_date):
	conditions = ''

	conditions += "{"
	conditions += '"deposit_date": ["between", ["{}", "{}"]]'.format(from_date, to_date)
	# conditions += ', "amount_bd": [">", "0"]'
	conditions += ', "bank_account": "{}"'.format(filters.get("bank_account"))
	conditions += ', "bank_deposit": 1'
	conditions += ', "docstatus": ["!=", "0"]'
	conditions += '}'

	return conditions

def get_conditions_credit_note(filters, from_date, to_date):
	conditions = ''

	conditions += "{"
	conditions += '"check_date_nc": ["between", ["{}", "{}"]]'.format(from_date, to_date)
	conditions += ', "bank_account": "{}"'.format(filters.get("bank_account"))
	conditions += ', "credit_note": 1'
	conditions += ', "docstatus": ["!=", "0"]'
	conditions += '}'

	return conditions

def get_conditions_debit_note(filters, from_date, to_date):
	conditions = ''

	conditions += "{"
	conditions += '"check_date_nd": ["between", ["{}", "{}"]]'.format(from_date, to_date)
	conditions += ', "bank_account": "{}"'.format(filters.get("bank_account"))
	conditions += ', "debit_note": 1'
	conditions += ', "docstatus": ["!=", "0"]'
	conditions += '}'

	return conditions

def get_conditions_check(filters, from_date, to_date):
	conditions = ''

	conditions += "{"
	conditions += '"check_date": ["between", ["{}", "{}"]]'.format(from_date, to_date)
	conditions += ', "bank_account": "{}"'.format(filters.get("bank_account"))
	conditions += ', "check": 1'
	conditions += ', "docstatus": ["!=", "0"]'
	conditions += '}'

	return conditions
