// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('NTHKO Potong', {
	refresh: function(frm) {
		frm.set_query("area_tujuan",function(){
	        return{
	            "filters": {
	                "is_standart" : 1
	            }
	        }
	    })
	}
});
