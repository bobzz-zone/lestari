// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Janji Bayar', {
	
	refresh: function(frm) {
		frm.events.make_custom_buttons(frm);
		if(!frm.doc.tutupan){
			frappe.call({
				method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
				args:{type:frm.doc.type_emas},
				callback: function (r){
					frm.doc.tutupan=r.message.nilai;
					refresh_field("tutupan")

				}
			})
		}
		frm.set_query("gold_invoice", function(){
			return {
				"filters": [
					// ["Gold Invoice", "customer", "=", cur_frm.doc.customer],
					["Gold Invoice", "outstanding", ">", 0.000]
				]
			}
		});
	},
	type_emas:function(frm){
		frm.doc.stock_deposit=[];
		refresh_field("stock_deposit");
		frappe.call({
			method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
			args:{type:frm.doc.type_emas},
			callback: function (r){
				frm.doc.tutupan=r.message.nilai;
				refresh_field("tutupan");
			}
		});
	},
	validate:function(frm){
		cur_frm.set_value("total_emas", cur_frm.doc.total_bayar / cur_frm.doc.tutupan);
	},
	gold_invoice: function(frm){
		var total_idr = 0;
		total_idr = cur_frm.doc.total_invoice * cur_frm.doc.tutupan
		cur_frm.set_value("total_idr_payment", total_idr)
		cur_frm.refresh_field("total_idr_payment")
	},
	total_bayar:function(frm){
		cur_frm.set_value("total_emas", cur_frm.doc.total_bayar / cur_frm.doc.tutupan);
		cur_frm.refresh_field("total_emas");
	},
	tutupan: function(frm){
		if(frm.doc.jenis_janji=="Pembayaran"){
			var total_idr = 0;
			total_idr = cur_frm.doc.total_invoice * cur_frm.doc.tutupan;
			cur_frm.set_value("total_idr_payment", total_idr);
			cur_frm.refresh_field("total_idr_payment");
		}
		cur_frm.set_value("total_emas", cur_frm.doc.total_bayar / cur_frm.doc.tutupan);
		cur_frm.refresh_field("total_emas");
		

	},
	make_custom_buttons: function (frm) {
	if (frm.doc.docstatus === 1 && frm.doc.status==="Pending" && frm.doc.jenis_janji==="Pembayaran") {
	  frm.add_custom_button(__("Quick Payment"), () => frm.events.get_gold_payment(frm));
	}else if (frm.doc.docstatus === 1 && frm.doc.status==="Pending" && frm.doc.jenis_janji==="Deposit"){
		frm.add_custom_button(__("Quick Deposit"), () => frm.events.get_deposit(frm));
	}
  },
  get_gold_payment: function (frm) {
	frm.call("get_gold_payment", { throw_if_missing: true }).then((r) => {
	  if (r.message) {
		console.log(r.message);
		frappe.set_route("Form", r.message.doctype, r.message.name);
	  }
	});
  },
  get_deposit: function (frm) {
	frm.call("get_deposit", { throw_if_missing: true }).then((r) => {
	  if (r.message) {
		console.log(r.message);
		frappe.set_route("Form", r.message.doctype, r.message.name);
	  }
	});
}
});
