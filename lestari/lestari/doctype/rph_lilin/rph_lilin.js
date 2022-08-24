// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("RPH Lilin", {
  refresh: function (frm) {
    frm.events.make_custom_buttons(frm);
  },
  make_custom_buttons: function (frm) {
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(__("Ambil SPK Produksi"), () => frm.events.get_items_from_spk_produksi(frm));
    }
  },
  get_items_from_spk_produksi: function (frm) {
    erpnext.utils.map_current_doc({
      method: "lestari.lestari.doctype.rph_lilin.rph_lilin.get_items_from_spk_produksi",
      source_doctype: "SPK Produksi",
      target: frm,
      setters: {
        area: undefined,
        // no_spk: frm.doc.no_spk || undefined,
        // kadar: frm.doc.kadar || undefined,
        // produk_id: frm.doc.produk_id || undefined,
      },
      get_query_filters: {
        docstatus: 1,
        // status: ["not in", ["Cancel"]],
        company: frm.doc.company,
      },
      allow_child_item_selection: true,
      child_fielname: "tabel_rencana_produksi",
      child_columns: ["produk_id", "qty", "kategori", "sub_kategori", "kadar"],
    });
  },
});
// ($("element").data("bs.modal") || {})._isShown;
// $(document).is(":visible", ".modal-dialog", function () {
//   $(this).css("max-width", "800px");
// alert("test");
// console.log("test");
// });
// if ($(document).data(".modal-dialog").isShown) {
// alert("test");
// }

// frappe.ui.form.on('RPH Lilin Detail', {
// 	tabel_detail_add: function(frm, cdt, cdn){
// 		frappe.msgprint("Hallo")
// 	}
// });
