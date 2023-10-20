// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('NTHKO Inject Lilin', {
	refresh: function(frm) {
		$('div[data-fieldname="item_button"').on('click',function(){
			frm.set_df_property('item_section', 'hidden', 0)
			frm.set_df_property('penggunaan_batu_section', 'hidden', 1)
		})
		$('div[data-fieldname="penggunaan_batu"').on('click',function(){
			frm.set_df_property('item_section', 'hidden', 1)
			frm.set_df_property('penggunaan_batu_section', 'hidden', 0)
		})
	},
	id_operator: function(frm){
		frappe.db.get_value("Employee", { "id_employee": cur_frm.doc.id_operator, "department": "Lilin - LMS" }, ["name","employee_name"]).then(function (responseJSON) {
			if(responseJSON.message.employee_name){
				cur_frm.set_value("nama_operator", responseJSON.message.employee_name);
				cur_frm.set_value("operator", responseJSON.message.name);
				cur_frm.refresh_field("nama_operator");
				cur_frm.refresh_field("operator");
			}
		})
	}
});
