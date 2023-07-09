// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Generator', {
	// setup: function(frm){
		// if (frm.is_new()) {
			// frappe.db.get_list("Data Logam").then((data) => {
			// 	// console.log(kadar);
			// 	$.each(data, function (key, value){
			// 		console.log(value.name);
			// 		cur_frm.add_child('tabel_kadar').kadar = value.name;
			// 	});
			// 	cur_frm.refresh_field('tabel_kadar');
			// });
			// frm.call
		// }
	// }
	// refresh: function(frm) {

	// }
	before_save: function(frm){
		// frappe.msgprint('hallooo')
		var item_code;
		if(cur_frm.doc.item_code){
			item_code = cur_frm.doc.item_code
		}else{
			item_code = cur_frm.doc.item_code_from_items
		}
		cur_frm.set_value("naming_series", item_code)
		cur_frm.refresh_field('naming_series')
	}
});
