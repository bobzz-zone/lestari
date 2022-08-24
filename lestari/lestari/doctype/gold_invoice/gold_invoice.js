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
	}
})