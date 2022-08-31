// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Deposit', {
	refresh: function(frm) {
		frm.set_query("item","stock_deposit", function(doc, cdt, cdn) {
    			return {
    				"filters": {
    					"available_for_stock_payment":1
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
	}
});
frappe.ui.form.on('IDR Payment', {
	amount:function(frm,cdt,cdn) {
		var total=0;
		$.each(frm.doc.idr_deposit,  function(i,  g) {
		   	total=total+g.amount;
		});
		frm.doc.total_idr_deposit=total;
		frm.doc.idr_left=total;
		refresh_field("total_idr_deposit");
		refresh_field("idr_left");
	}
});
frappe.ui.form.on('Stock Payment', {
	item:function(frm,cdt,cdn) {
		// your code here
		var d=locals[cdt][cdn];
		if(!d.item_group){return;}
		frappe.call({
                method: "lestari.lestari.doctype.gold_invoice.gold_invoice.get_gold_purchase_rate",
                args:{"item_group":d.item_group,"customer":frm.doc.customer,"customer_group":frm.doc.customer_group},
                callback: function (r){
                    frappe.model.set_value(cdt, cdn,"rate",r.message.nilai);
                    frappe.model.set_value(cdt, cdn,"amount",parseFloat(r.message.nilai)*d.qty);
                	var total=0;
				    $.each(frm.doc.stock_deposit,  function(i,  g) {
				    	total=total+g.amount;
				    });
				    frm.doc.total_gold_deposit=total;
				    frm.doc.gold_left=total;
				    refresh_field("total_gold_deposit");
				    refresh_field("gold_left");
                	}
                });
		
	},
	qty:function(frm,cdt,cdn) {
	    var d=locals[cdt][cdn];
	    frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty);
	    var total=0;
		$.each(frm.doc.stock_deposit,  function(i,  g) {
		   	total=total+g.amount;
		});
		frm.doc.total_gold_deposit=total;
		frm.doc.gold_left=total;
		refresh_field("total_gold_deposit");
		refresh_field("gold_left");
	}
	
});
