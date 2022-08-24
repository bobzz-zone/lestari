// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rencana Form Order Produksi", {
  // refresh: function(frm) {
  // }
  //   onload: function (frm) {},
});

frappe.ui.form.on("Rencana Form Order Produksi Order", {
  type_order: function (frm, cdt, cdn) {
    frappe.msgprint("Type Order");
    var row = locals[cdt][cdn];
    if (row.type_order) {
      if (!frm.doc.type_order) {
        erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "tabel_order", "type_order");
      }
      //   else {
      //     set_schedule_date(frm);
      //   }
    }
  },
  tabel_order_add: function (doc, cdt, cdn) {
    frappe.msgprint("Tabel Add");
    var row = locals[cdt][cdn];
    console.log(row);
    row.type_order = cur_frm.doc.type_order;
    cur_frm.refresh_field("tabel_order");
  },
  tabel_order_update: function (doc, cdt, cdn) {
    frappe.msgprint("Tabel Update");
  },
  tabel_order_delete: function (doc, cdt, cdn) {
    frappe.msgprint("Tabel Delete");
  },
});

function tambah_tabel(frm) {
  var a = frappe.model.add_child(cur_frm.doc, "Rencana Form Order Produksi Order", "tabel_order");
  a.type_order = cur_frm.doc.type_order;
  frm.refresh_field("tabel_order");
}
