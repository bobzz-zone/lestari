// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('RPH BSP', {
	setup: function (frm) {
		frappe.db.get_value("Employee", { user_id: frappe.session.user }, "name").then(function (responseJSON) {
		  cur_frm.set_value("employee_id", responseJSON.message.name);
		  cur_frm.refresh_field("employee_id");
		});
	  },
	  refresh: function (frm) {
		frm.events.make_custom_buttons(frm);
	  },
	  make_custom_buttons: function (frm) {
		if (frm.doc.docstatus === 0) {
		  frm.add_custom_button(__("Ambil Transfer Material"), () => frm.events.get_items_from_transfer_material(frm));
		}
	  },
	  get_items_from_transfer_material: function (frm) {
		erpnext.utils.map_current_doc({
		  method: "lestari.lestari.doctype.rph_bsp.rph_bsp.get_items_from_transfer_material",
		  source_doctype: "Transfer Material",
		  target: frm,
		  setters: {
			area: undefined,
			// no_spk: frm.doc.no_spk || undefined,
			// kadar: frm.doc.kadar || undefined,
			// produk_id: frm.doc.produk_id || undefined,
		  },
		  size: "extra-large",
		  get_query_filters: {
			docstatus: 1,
			status: ["not in", ["Cancel"]],
			// company: frm.doc.company,
		  },
		  allow_child_item_selection: true,
		  child_fieldname: "transfer_detail",
		  child_columns: ["nthko_area", "nthko_id", "s_warehouse", "t_warehouse"],
		});
	  },
	});
