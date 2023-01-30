// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Update Bundle Stock', {
	// refresh: function(frm) {

	// }
});
frappe.ui.form.on('Detail Penambahan Stock', {
	items_add: function (frm, cdt, cdn){
		frappe.msgprint('Test')
	},
	category: function (frm, cdt, cdn) {
		// your code here
		var d = locals[cdt][cdn];
		if (!d.category) {
		  return;
		}
	} 
});
