# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
	filters["invoices"] = frappe.cache().hget("invoices", frappe.session.user)
	validate_filters(filters)
	set_filters(filters)

	columns = get_columns()
	res = get_result(filters)

	return columns, res

def validate_filters(filters):
	''' Validate if dates are properly set '''
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def set_filters(filters):
	invoices = []

	if not filters["invoices"]:
		filters["invoices"] = get_tds_invoices()
	if filters.supplier and filters.purchase_invoice:
		for d in filters["invoices"]:
			if d.name == filters.purchase_invoice and d.supplier == filters.supplier:
				invoices.append(d)
	elif filters.supplier and not filters.purchase_invoice:
		for d in filters["invoices"]:
			if d.supplier == filters.supplier:
				invoices.append(d)
	elif filters.purchase_invoice and not filters.supplier:
		for d in filters["invoices"]:
			if d.name == filters.purchase_invoice:
				invoices.append(d)

	filters["invoices"] = invoices if invoices else filters["invoices"]

def get_result(filters):
	supplier_map, tds_docs = get_supplier_map(filters)
	gle_map = get_gle_map(filters)

	out = []
	for d in gle_map:
		tds_deducted, total_amount_credited = 0, 0
		supplier = supplier_map[d]

		tds_doc = tds_docs[supplier.tax_withholding_category]
		account = [i.account for i in tds_doc.accounts if i.company == filters.company][0]

		for k in gle_map[d]:
			if k.party == supplier_map[d] and k.credit > 0:
				total_amount_credited += k.credit
			elif k.account == account and k.credit > 0:
				tds_deducted = k.credit
				total_amount_credited += k.credit

		rate = [i.tax_withholding_rate for i in tds_doc.rates
			if i.fiscal_year == gle_map[d][0].fiscal_year][0]

		if getdate(filters.from_date) <= gle_map[d][0].posting_date \
			and getdate(filters.to_date) >= gle_map[d][0].posting_date:
			out.append([supplier.pan, supplier.name, tds_doc.name,
				supplier.supplier_type, rate, total_amount_credited, tds_deducted,
				gle_map[d][0].posting_date, "Purchase Invoice", d])

	return out

def get_supplier_map(filters):
	# create a supplier_map of the form {"purchase_invoice": {supplier_name, pan, tds_name}}
	# pre-fetch all distinct applicable tds docs
	supplier_map, tds_docs = {}, {}
	pan = "pan" if frappe.db.has_column("Supplier", "pan") else "tax_id"
	supplier_detail = frappe.db.get_all('Supplier',
		{"name": ["in", [d.supplier for d in filters["invoices"]]]},
		["tax_withholding_category", "name", pan+" as pan", "supplier_type"])

	for d in filters["invoices"]:
		supplier_map[d.get("name")] = [k for k in supplier_detail
			if k.name == d.get("supplier")][0]

	for d in supplier_detail:
		if d.get("tax_withholding_category") not in tds_docs:
			tds_docs[d.get("tax_withholding_category")] = \
				frappe.get_doc("Tax Withholding Category", d.get("tax_withholding_category"))

	return supplier_map, tds_docs

def get_gle_map(filters):
	# create gle_map of the form
	# {"purchase_invoice": list of dict of all gle created for this invoice}
	gle_map = {}
	gle = frappe.db.get_all('GL Entry',\
		{"voucher_no": ["in", [d.get("name") for d in filters["invoices"]]]},
		["fiscal_year", "credit", "debit", "account", "voucher_no", "posting_date"])

	for d in gle:
		if not d.voucher_no in gle_map:
			gle_map[d.voucher_no] = [d]
		else:
			gle_map[d.voucher_no].append(d)

	return gle_map

def get_columns():
	pan = "pan" if frappe.db.has_column("Supplier", "pan") else "tax_id"
	columns = [
		{
			"label": _(frappe.unscrub(pan)),
			"fieldname": pan,
			"fieldtype": "Data",
			"width": 90
		},
		{
			"label": _("Supplier"),
			"options": "Supplier",
			"fieldname": "supplier",
			"fieldtype": "Link",
			"width": 180
		},
		{
			"label": _("Section Code"),
			"options": "Tax Withholding Category",
			"fieldname": "section_code",
			"fieldtype": "Link",
			"width": 180
		},
		{
			"label": _("Entity Type"),
			"fieldname": "entity_type",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("TDS Rate %"),
			"fieldname": "tds_rate",
			"fieldtype": "Float",
			"width": 90
		},
		{
			"label": _("Total Amount Credited"),
			"fieldname": "total_amount_credited",
			"fieldtype": "Float",
			"width": 90
		},
		{
			"label": _("Amount of TDS Deducted"),
			"fieldname": "tds_deducted",
			"fieldtype": "Float",
			"width": 90
		},
		{
			"label": _("Date of Transaction"),
			"fieldname": "transaction_date",
			"fieldtype": "Date",
			"width": 90
		},
		{
			"label": _("Transaction Type"),
			"fieldname": "transaction_type",
			"width": 90
		},
		{
			"label": _("Reference No."),
			"fieldname": "ref_no",
			"fieldtype": "Dynamic Link",
			"options": "transaction_type",
			"width": 90
		}
	]

	return columns

@frappe.whitelist()
def get_tds_invoices():
	# fetch tds applicable supplier and fetch invoices for these suppliers
	suppliers = [d.name for d in frappe.db.get_list("Supplier",
		{"tax_withholding_category": ["!=", ""]}, ["name"])]

	invoices = frappe.db.get_list("Purchase Invoice",
		{"supplier": ["in", suppliers]}, ["name", "supplier"])

	frappe.cache().hset("invoices", frappe.session.user, invoices)

	return invoices
