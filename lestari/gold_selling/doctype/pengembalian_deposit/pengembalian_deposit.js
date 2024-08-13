// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pengembalian Deposit', {
	refresh: function(frm) {
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
		if(frm.doc.docstatus > 0) {
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
					company: frm.doc.company,
					group_by: "Group by Voucher (Consolidated)",
					show_cancelled_entries: frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
		frm.set_query("deposit", function (doc, cdt, cdn) {
			return {
				query: "lestari.gold_selling.doctype.customer_deposit.customer_deposit.get_deposit_outstanding",
				filters: { customer: doc.customer ,subcustomer:doc.subcustomer},
			};
		});
	}
});
