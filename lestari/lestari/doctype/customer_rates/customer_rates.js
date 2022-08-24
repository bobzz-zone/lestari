// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Rates', {
	refresh(frm) {
		frm.set_query("item_group", function(doc) {
    			return {
    				"filters": {
    					"parent_item_group":"Penjualan"
    				}
    			};
    		});
	 }
});
