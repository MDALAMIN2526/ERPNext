# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class DepartmentApprover(Document):
	pass

@frappe.whitelist()
def get_approvers(doctype, txt, searchfield, start, page_len, filters):

	if not filters.get("employee"):
		frappe.throw(_("Please select Employee Record first."))

	approvers = []
	department_details = {}
	department_list = []
	employee_department = filters.get("department") or frappe.get_value("Employee", filters.get("employee"), "department")
	if employee_department:
		department_details = frappe.db.get_value("Department", {"name": employee_department}, ["lft", "rgt"], as_dict=True)
	if department_details:
		department_list = frappe.db.sql("""select name from `tabDepartment` where lft <= %s
			and rgt >= %s
			and disabled=0
			order by lft desc""", (department_details.lft, department_details.rgt), as_list=True)

	leave_approver = frappe.get_cached_value('Employee', filters.get('employee'), 'leave_approver')
	if leave_approver:
		approver = frappe.db.get_value("User", leave_approver, ['name', 'first_name', 'last_name'])
		approvers.append(approver)

	if filters.get("doctype") == "Leave Application":
		parentfield = "leave_approvers"
	else:
		parentfield = "expense_approvers"
	if department_list:
		for d in department_list:
			approvers += frappe.db.sql("""select user.name, user.first_name, user.last_name from
				tabUser user, `tabDepartment Approver` approver where
				approver.parent = %s
				and user.name like %s
				and approver.parentfield = %s
				and approver.approver=user.name""",(d, "%" + txt + "%", parentfield), as_list=True)

	return approvers