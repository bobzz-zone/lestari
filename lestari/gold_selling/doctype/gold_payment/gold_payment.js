// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gold Payment', {
	refresh: function(frm) {
		frm.set_query("item","stock_payment", function(doc, cdt, cdn) {
    			return {
    				"filters": {
    					"available_for_stock_payment":1
    				}
    			};

    		});
		frm.set_query("gold_invoice","invoice_table", function(doc, cdt, cdn) {
    			return {
    				"filters": {
    					"docstatus":1,
    					//"invoice_status":"Unpaid",
    					"customer":doc.customer
    				}
    			};

    		});
		if(!frm.doc.tutupan){
		    frappe.call({
                method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
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

frappe.ui.form.on('Gold Payment Invoice', {
	gold_invoice:function(frm,cdt,cdn) {
		var total=0;
		var allocated=0;
		$.each(frm.doc.invoice_table,  function(i,  g) {
		   	total=total+g.outstanding;
		   	allocated=allocated+g.allocated;
		});
		frm.doc.total_invoice=total;
		frappe.model.set_value(cdt, cdn,"allocated",0);
		refresh_field("allocated");
		refresh_field("total_invoice");
		frm.doc.allocated_payment=allocated;
		refresh_field("allocated_payment");

	},
	allocated:function(frm,cdt,cdn) {
		var allocated=0;
		$.each(frm.doc.invoice_table,  function(i,  g) {
		   	allocated=allocated+g.allocated;
		});
		frm.doc.allocated_payment=allocated;
		refresh_field("allocated_payment");
	}
});
frappe.ui.form.on('IDR Payment', {
	amount:function(frm,cdt,cdn) {
		var total=0;
		$.each(frm.doc.idr_payment,  function(i,  g) {
		   	total=total+g.amount;
		});
		frm.doc.total_idr_payment=total;
		frm.doc.total_idr_gold=total/frm.doc.tutupan;
		refresh_field("total_idr_payment");
		refresh_field("total_idr_gold");
		//calculate total payment
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("total_payment");
	}
});
frappe.ui.form.on('Stock Payment', {
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
				    $.each(frm.doc.stock_payment,  function(i,  g) {
				    	total=total+g.amount;
				    });
				    frm.doc.total_gold_payment=total;
				    refresh_field("total_gold_payment");
				    //calculate total payment
					frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
					refresh_field("total_payment");
				    }
                });
		
	},
	qty:function(frm,cdt,cdn) {
	    var d=locals[cdt][cdn];
	    frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty/100);
	    var total=0;
		$.each(frm.doc.stock_payment,  function(i,  g) {
		   	total=total+g.amount;
		});
		frm.doc.total_gold_payment=total;
		refresh_field("total_gold_payment");
		//calculate total payment
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("total_payment");
	}
	
});

