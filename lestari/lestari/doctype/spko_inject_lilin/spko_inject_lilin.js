// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('SPKO Inject Lilin', {
	refresh: function(frm) {
		frm.events.make_custom_buttons(frm);
	},
	make_custom_buttons: function (frm) {
		// if (frm.doc.docstatus === 0) {
		  // frm.add_custom_button(__("Sales Order"), () => frm.events.get_items_from_sales_order(frm), __("Get Items From"));
		  frm.add_custom_button(__("DAFTAR PRODUCT"), () => frm.events.get_items_from_rph_lilin(frm));
		  frm.add_custom_button(__("CETAK BARCODE"), () => frm.events.get_items_from_form_order(frm), __("CETAK"));
		  frm.add_custom_button(__("CETAK SPKO"), () => frm.events.get_items_from_form_order(frm), __("CETAK"));
		// }
	},
	get_items_from_rph_lilin: function (frm) {
		erpnext.utils.map_current_doc({
			// new frappe.ui.form.MultiSelectDialog({
			method: "lestari.lestari.doctype.spko_inject_lilin.spko_inject_lilin.get_items_from_rph_lilin",
			source_doctype: "RPH Lilin",
			// doctype: "Form Order",
			// doctype: "RPH Lilin Detail",
			target: frm,
			setters: {
			//   name: me.frm.doc.rph_lilin
				// // parent: undefined,
				// no_spk: undefined,
				// kadar: undefined,
				// kategori : undefined,
				// sub_kategori : undefined,
				// qty: undefined
			},
			add_filters_group: 1,
			// columns: ["no_spk", "kadar", "kategori","sub_kategori","qty"],
			size: "extra-large",
			get_query_filters: {
			  docstatus: 1,
			  // status: ["not in", ["Cancel"]],
			  name: frm.doc.rph_lilin,
			  kadar: frm.doc.kadar			  
			},
			// action(selections) {
			// 	$.each(selections, function(i,g){
			// 		// console.log("i"+i);
			// 		// console.log("\ng"+g);
			// 		cur_frm.add_child('items', {
			// 			child_no: g,
			// 		});
					
			// 	})
			// 	cur_frm.refresh_field('items');
			// }
			allow_child_item_selection: true,
			// child_fieldname: "items_valid",
      		// child_columns: ["model", "item_name", "kadar", "kategori", "sub_kategori", "kategori_pohon", "qty_isi_pohon", "no_pohon", "qty"],
			child_fieldname: "tabel_detail",
			child_columns: [
			"no_spk",
			"kadar",
			"kategori"	
			],
		  });
	}
});