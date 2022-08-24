// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('RPH Campur Bahan', {
	setup: function (frm) {
		frm.call({
		  method: "get_current_stock",
		  doc: frm.doc,
		  callback: function (r) {
			console.log(r.message);
			cur_frm.set_df_property("stock_level", "options", r.message);
			frappe.msgprint(__("Success Get Current Stock"));
			frm.refresh_field("stock_level");
		  },
		});
	  },
	  get_data: function (frm) {
		frm.call({
		  method: "get_current_stock",
		  doc: frm.doc,
		  callback: function (r) {
			console.log(r.message);
			cur_frm.set_df_property("stock_level", "options", r.message);
			frappe.msgprint(__("Success Get Current Stock"));
			frm.refresh_field("stock_level");
		  },
		});
	  },
	refresh: function(frm) {
		frm.set_query("product_id",function(){
	        return{
	            "filters": {
	                "warehouse" : 'Campur Bahan - L'
	            }
	        }
	    })
	}
});
