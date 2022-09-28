// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Payment Return', {
	refresh: function(frm) {
		frm.set_query("item","items", function(doc, cdt, cdn) {
    			return {
    				"filters": {
    					"available_for_stock_payment":1
    				}
    			};

    		});
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
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: me.frm.doc.name,
					from_date: me.frm.doc.posting_date,
					to_date: moment(me.frm.doc.modified).format('YYYY-MM-DD'),
					company: me.frm.doc.company,
					show_cancelled_entries: me.frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "Stock Ledger");
			}, __("View"));
		}
	}
});
frappe.ui.form.on('Stock Payment Return Item', {
	item:function(frm,cdt,cdn) {
		// your code here
		var d=locals[cdt][cdn];
		if(!d.item){return;}
		frappe.call({
                method: "lestari.gold_selling.doctype.gold_invoice.gold_invoice.get_gold_purchase_rate",
                args:{"item":d.item,"customer":frm.doc.customer,"customer_group":frm.doc.customer_group},
                callback: function (r){
                    frappe.model.set_value(cdt, cdn,"rate",r.message.nilai);
                    frappe.model.set_value(cdt, cdn,"amount",parseFloat(r.message.nilai)*d.qty/100);
                	var total=0;
				    $.each(frm.doc.stock_deposit,  function(i,  g) {
				    	total=total+g.amount;
				    });
			    	frm.doc.total=total;
				    refresh_field("total");
                	}
                });
		
	},
	qty:function(frm,cdt,cdn) {
	    var d=locals[cdt][cdn];
	    frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty/100);
	    var total=0;
		$.each(frm.doc.stock_deposit,  function(i,  g) {
		   	total=total+g.amount;
		});
		frm.doc.total=total;
		
		refresh_field("total");
	}
	
});