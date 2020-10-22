# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils import nowdate
from datetime import date

class TestAttendanceRequest(unittest.TestCase):
	def setUp(self):
		for doctype in ["Attendance Request", "Attendance"]:
			frappe.db.sql("delete from `tab{doctype}`".format(doctype=doctype))

	def test_attendance_request_aproval_and_cancelation(self):
		today = nowdate()
		employee = get_employee()
		attendance_request = frappe.new_doc("Attendance Request")
		attendance_request.employee = employee.name
		attendance_request.from_date = date(date.today().year, 1, 1)
		attendance_request.to_date = date(date.today().year, 1, 2)
		attendance_request.status = "Present"
		attendance_request.company = "_Test Company"
		attendance_request.insert()
		attendance_request.submit()
		attendance = frappe.get_doc('Attendance', {
			'employee': employee.name,
			'attendance_request': attendance_request.name,
			'docstatus': 1
		})
		self.assertEqual(attendance.status, 'Present')
		attendance_request.cancel()
		attendance.reload()
		self.assertEqual(attendance.docstatus, 2)

	def tearDown(self):
		frappe.db.sql("""DELETE FROM `tabAttendance Request`""")
		frappe.db.sql("""DELETE FROM `tabAttendance` where attendance_request IS NOT NULL or attendance_request = '' """)

def get_employee():
	return frappe.get_doc("Employee", "_T-Employee-00001")