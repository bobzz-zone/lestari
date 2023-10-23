// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('SPKO Inject Lilin', {
	refresh: function(frm) {
		frm.events.make_custom_buttons(frm);

		$('div[data-fieldname="item_button"').on('click',function(){
			frm.set_df_property('item_section', 'hidden', 0)
			frm.set_df_property('karet_pilihan_section', 'hidden', 1)
		})
		$('div[data-fieldname="karet_pilihan"').on('click',function(){
			frm.set_df_property('item_section', 'hidden', 1)
			frm.set_df_property('karet_pilihan_section', 'hidden', 0)
		})
		$('div[data-fieldname="daftar_product"').on('click',function(){
			frm.events.get_items_from_rph_lilin(frm)
		})
	},
	make_custom_buttons: function (frm) {
		// if (frm.doc.docstatus === 0) {
		  frm.add_custom_button(__("DAFTAR PRODUCT"), () => frm.events.get_items_from_rph_lilin(frm));
		  frm.add_custom_button(__("CETAK BARCODE"), () => frm.events.get_items_from_form_order(frm), __("CETAK"));
		  frm.add_custom_button(__("CETAK SPKO"), () => frm.events.get_items_from_form_order(frm), __("CETAK"));
		// }
	},
	id_operator: function (frm){
		frappe.db.get_value("Employee", { "id_employee": cur_frm.doc.id_operator, "department": "Lilin - LMS" }, ["name","employee_name"]).then(function (responseJSON) {
			if(responseJSON.message.employee_name){
				cur_frm.set_value("nama_operator", responseJSON.message.employee_name);
				cur_frm.set_value("operator", responseJSON.message.name);
				cur_frm.refresh_field("nama_operator");
				cur_frm.refresh_field("operator");
			}
		})
	},
	
	get_items_from_rph_lilin: async function (frm) {
		var r = await erpnext.utils.map_current_doc({
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
			  name: frm.doc.rph_lilin || undefined,
			  kadar: frm.doc.kadar || undefined			  
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
		  $(document).on("frappe.ui.Dialog:shown", function() {
			// Your custom logic here, e.g., perform some action when the dialog is shown
			if(!r.dialog.fields_dict['allow_child_item_selection'].get_value()){
				r.dialog.fields_dict.allow_child_item_selection.$input.click()
			}
	  
			if($(":input[data-fieldname='allow_child_item_selection']").is(':checked')){
			  setTimeout(function(){
				console.log(r.child_datatable)
				$(":input[data-name='Kadar']").val(cur_frm.doc.kadar);
				console.log(r.child_datatable.columnmanager.applyFilter(r.child_datatable.columnmanager.getAppliedFilters())) 
			  }, 2000)
			}
		  });
	}
});

