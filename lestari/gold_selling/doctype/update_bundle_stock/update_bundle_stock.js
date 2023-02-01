// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

function hitung(frm){
	$.each(frm.doc.item, function(i,e){
		console.log(e)
	})
}
frappe.ui.form.on('Update Bundle Stock', {
	// refresh: function(frm) {

	// }
});
frappe.ui.form.on('Detail Penambahan Stock', {
	items_add: function (frm, cdt, cdn){
		hitung(frm)
	},
	sub_kategori: function (doc,cdt, cdn){
		var d = locals[cdt][cdn];
		frappe.call({
			method: 'lestari.gold_selling.doctype.update_bundle_stock.update_bundle_stock.get_sub_item',
			args: {
				'kadar': d.kadar,
				'sub_kategori': d.sub_kategori
			},
			callback: function(r) {
				if (!r.exc) {
					d.item = r.message[0][0]
					d.gold_selling_item = r.message[0][1]
					cur_frm.refresh_field("items")
				}
			}
		});
	}, 
});
