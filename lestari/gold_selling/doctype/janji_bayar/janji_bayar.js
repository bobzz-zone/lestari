// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Janji Bayar', {
	
	refresh: function(frm) {
		frm.events.make_custom_buttons(frm);
		frm.set_query("gold_invoice", function(){
			return {
				"filters": [
					["Gold Invoice", "customer", "=", cur_frm.doc.customer],
					["Gold Invoice", "outstanding", ">", 0.000]
				]
			}
		});
	},
	gold_invoice: function(frm){
		var total_idr = 0;
		total_idr = cur_frm.doc.total_invoice * cur_frm.doc.tutupan
		cur_frm.set_value("total_idr_payment", total_idr)
		cur_frm.refresh_field("total_idr_payment")
	},
	tutupan: function(frm){
		var total_idr = 0;
		total_idr = cur_frm.doc.total_invoice * cur_frm.doc.tutupan
		cur_frm.set_value("total_idr_payment", total_idr)
		cur_frm.refresh_field("total_idr_payment")
	},
	make_custom_buttons: function (frm) {
	if (frm.doc.docstatus === 1 && frm.doc.status==="Pending") {
	  frm.add_custom_button(__("Quick Payment"), () => frm.events.get_gold_payment(frm));
	}
  },
  get_gold_payment: function (frm) {
	frm.call("get_gold_payment", { throw_if_missing: true }).then((r) => {
	  if (r.message) {
		console.log(r.message);
		frappe.set_route("Form", r.message.doctype, r.message.name);
	  }
	});
  }
});
