// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("SPK Produksi", {
  refresh: function(frm) {

  // }
  // area: function (frm) {
  //   frm.clear_custom_buttons();
    frm.events.make_custom_buttons(frm);
  },
  make_custom_buttons: function (frm) {
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(__("Sales Order"), () => frm.events.get_items_from_sales_order(frm), __("Get Items From"));
    }
  },
  get_items_from_sales_order: function (frm) {
    erpnext.utils.map_current_doc({
      method: "lestari.lestari.doctype.spk_produksi.spk_produksi.make_material_request",
      source_doctype: "Sales Order",
      target: frm,
      setters: {
        customer: frm.doc.customer || undefined,
        delivery_date: undefined,
        currency: frm.doc.currency || undefined,
        order_type: frm.doc.order_type || undefined
      },
      size: "extra-large",
      add_filters_group: 1,
      get_query_filters: {
        docstatus: 1,
        status: ["not in", ["Closed", "On Hold"]],
        per_delivered: ["<", 99.99],
        company: frm.doc.company,
      },
      allow_child_item_selection: true,
      child_fieldname: "items",
      child_columns: ["parent", "item_code", "qty", "qty_isi_pohon", "jumlah_pohon", "target_berat"],
    });
  },
  //   get_items_from_material_request: function (frm) {
  //     erpnext.utils.map_current_doc({
  //       method: "lestari.lestari.doctype.spk_produksi.spk_produksi.get_material_request",
  //       source_doctype: "Material Request",
  //       target: frm,
  //       setters: {
  //         transaction_date: undefined,
  //         schedule_date: undefined,
  //         status: undefined,
  //       },
  //       get_query_filters: {
  //         docstatus: 1,
  //         status: ["!=", "Stopped"],
  //         per_ordered: ["<", 100],
  //         company: me.frm.doc.company,
  //       },
  //     });
  //   },
});
