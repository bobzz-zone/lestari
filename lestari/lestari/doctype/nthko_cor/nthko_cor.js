// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('NTHKO Cor', {
	refresh: function(frm) {
		frm.set_query("work_order_id",function(){
	        return{
	            "filters": {
					"docstatus" : 1
	            }
	        }
	    }),
		frm.set_query("pohon_id",function(){
	        return{
	            "filters": {
					"warehouse": "Gips - L"
	            }
	        }
	    })
	}
});
