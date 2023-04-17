// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

var list_kat = [];
frappe.ui.form.on('Konfirmasi Payment Return', {
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
		frm.set_query("sub_kategori", "detail_perhiasan", function () {
			return {
				"filters": [
					["Item Group", "parent_item_group", "in", list_kat],
				]
			};
		  });
	},
	serah_terima: function(frm) {
		frappe.call({
			method: "get_serah_terima",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();	
				}
			})
	}
});

frappe.ui.form.on('Konfirmasi Payment Return Rongsok', {
	terima_qty: function(frm, cdt, cdn){
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"tolak_qty",d.qty-d.terima_qty);
		frappe.model.set_value(cdt, cdn,"total_berat",d.terima_qty+d.tolak_qty);
	},
	tolak_qty: function(frm, cdt, cdn){
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"terima_qty",d.qty-d.terima_qty);
		frappe.model.set_value(cdt, cdn,"total_berat",d.tolak_qty+d.terima_qty);
	}
});
