// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Order Potong', {
	refresh: function(frm) {
		frm.set_query("pohon_id",function(){
	        return{
	            "filters": {
	                "warehouse" : 'Cor - L'
	            }
	        }
	    })
	}
});
