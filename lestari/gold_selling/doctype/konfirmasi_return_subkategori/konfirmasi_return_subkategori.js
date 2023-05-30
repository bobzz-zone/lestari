// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

var list_kat = [];
frappe.ui.form.on('Konfirmasi Return Subkategori', {
	refresh: function(frm) {
		frappe.db.get_list('Item Group', {
			filters: {
				parent_item_group: 'Products'
			}
		}).then(records => {
			for(var i = 0; i<= records.length; i++){
				list_kat.push(records[i].name)
			}
		})
		frm.set_query("sub_kategori", "items", function () {
			return {
				"filters": [
					["Item Group", "parent_item_group", "in", list_kat],
				]
			};
		  });
	},no_konfirmasi: function(frm){
		frappe.call({
			method: "get_konfirmasi",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();	
				}
			})
	}
});
