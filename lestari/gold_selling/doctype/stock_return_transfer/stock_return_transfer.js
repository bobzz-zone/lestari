// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Return Transfer', {
	// refresh: function(frm) {

	// }
	get_details: function(frm){
		frappe.call({
			method: "get_kpr",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();	
				}
			})
	}
});
