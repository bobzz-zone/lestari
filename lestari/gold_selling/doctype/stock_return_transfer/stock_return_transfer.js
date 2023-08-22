// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Return Transfer', {
	refresh: function(frm) {
		frm.set_query("sub_customer", function (doc) {
			return {
			filters: {
				parent_customer: ["!=",""],
			},
			};
		});
	},
	get_details: function(frm){
		if(cur_frm.doc.transfer_details){
				cur_frm.clear_table("transfer_details")
				cur_frm.refresh_fields()
		}
		frappe.call({
			method: "get_kpr",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();	
			}
		})
	},
	sub_customer: function(frm){
		frappe.db.get_value("Customer", cur_frm.doc.sub_customer, ["parent_customer"]).then((responseJSON)=>{
			frm.set_value("customer", responseJSON.message.parent_customer)
			frm.refresh_field("customer")
		})
	}
});
