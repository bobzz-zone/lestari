// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gold Invoice', {
	refresh(frm) {
		frm.set_query("item_group","items", function(doc, cdt, cdn) {
    			return {
    				"filters": {
    					"parent_item_group":"Penjualan"
    				}
    			};
    		});
		// your code here
		if(!frm.doc.tutupan){
		    frappe.call({
                method: "lestari.lestari.doctype.gold_rates.gold_rates.get_latest_rates",
                callback: function (r){
                    frm.doc.tutupan=r.message.nilai;
                    refresh_field("tutupan")
                
                	}
                })
		}
	},
	discount(frm){
		if(frm.total) {frappe.model.set_value("grand_total",frm.doc.total-frm.doc.discount);}
	}
});
frappe.ui.form.on('Gold Invoice Item', {
	item_group(frm,cdt,cdn) {
		// your code here
		var d=locals[cdt][cdn];
		frappe.call({
                method: "lestari.lestari.doctype.gold_invoice.gold_invoice.get_gold_rate",
                args:{"item_group":d.item_group,"customer":frm.doc.customer,"customer_group":frm.doc.customer_group},
                callback: function (r){
                    frappe.model.set_value(cdt, cdn,"rate",r.message.nilai);
                    frappe.model.set_value(cdt, cdn,"amount",parseFloat(r.message.nilai)*d.qty);
                	var total=0;
				    $.each(frm.doc.items,  function(i,  g) {
				    	total=total+g.amount;
				    });
				    frm.doc.total=total;
				    frm.doc.grand_total=frm.doc.total-frm.doc.discount;
				    refresh_field("total")
				    refresh_field("grand_total")
                	}
                });
		
	},
	qty(frm,cdt,cdn) {
	    var d=locals[cdt][cdn];
	    frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty);
	    var total=0;
	    $.each(frm.doc.items,  function(i,  g) {
	    	total=total+g.amount;
	    });
	    frm.doc.total=total;
	    frm.doc.grand_total=frm.doc.total-frm.doc.discount;
	    refresh_field("total")
	    refresh_field("grand_total")
	}
});
