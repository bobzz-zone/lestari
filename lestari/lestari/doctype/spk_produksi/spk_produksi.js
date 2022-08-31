// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("SPK Produksi", {
  // refresh: function(frm) {

  // }
  area: function (frm) {
    frm.clear_custom_buttons();
    frm.events.make_custom_buttons(frm);
  },
  make_custom_buttons: function (frm) {
    // if (frm.doc.docstatus === 0 && frm.doc.area === "Lilin - L") {
    //   // frm.remove_custome_button("Form Hasil WO", "Get Item From");
    //   frm.add_custom_button(__("Material Request"), () => frm.events.get_items_from_material_request(frm), __("Get Items From"));
    // }
    if (frm.doc.docstatus === 0 && frm.doc.area === "Lilin - L") {
      frm.add_custom_button(__("Sales Order"), () => frm.events.get_items_from_sales_order(frm), __("Get Items From"));
    }
    if (frm.doc.docstatus === 0 && frm.doc.area === "GCP - L") {
      frappe.msgprint("test");
      // frm.remove_custome_button(["Form Hasil WO", "Sales Order"], "Get Item From");
      frm.add_custom_button(__("Form Hasil WO"), () => frm.events.get_items_form_hasil_wo(frm), __("Get Items From"));
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
      },
      size: "extra-large",
      get_query_filters: {
        docstatus: 1,
        status: ["not in", ["Closed", "On Hold"]],
        per_delivered: ["<", 99.99],
        company: frm.doc.company,
      },
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
