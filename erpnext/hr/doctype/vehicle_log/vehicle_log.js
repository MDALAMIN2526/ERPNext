// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Log", {
	refresh: function(frm) {
		// if(frm.doc.docstatus == 1) {
		// 	frm.add_custom_button(__('Expense Claim'), function() {
		// 		frm.events.expense_claim(frm);
		// 	}, __('Create'));
		// 	frm.page.set_inner_btn_group_as_primary(__('Create'));
		// }
	},

	expense_claim: function(frm){
		frappe.call({
			method: "erpnext.hr.doctype.vehicle_log.vehicle_log.make_expense_claim",
			args:{
				docname: frm.doc.name
			},
			callback: function(r){
				var doc = frappe.model.sync(r.message);
				frappe.set_route('Form', 'Expense Claim', r.message.name);
			}
		});
	},

	vehicle_log_type: function (frm){
		if (frm.doc.vehicle_log_type == 'Routine Checkup'){
			frm.set_df_property('service_detail','reqd',0);
			var field = frappe.meta.get_docfield("Vehicle Service", "item_code", frm.doc.name);
			field.reqd = 0;
		}else{
			var field = frappe.meta.get_docfield("Vehicle Service", "item_code", frm.doc.name);
			field.reqd = 1;
			frm.set_df_property('service_detail','reqd',1);
		}
		refresh_field('service_detail');
	},
	
});


