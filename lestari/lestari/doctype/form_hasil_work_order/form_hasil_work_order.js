// Copyright (c) 2021, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Form Hasil Work Order", {
  // refresh: function(frm) {

  // }
  total_berat_pohon_lilin: function (frm) {
    var berat_lilin = 0;
    frappe.msgprint(this);
    berat_lilin = cur_frm.doc.total_berat_pohon_lilin - (cur_frm.doc.total_berat_base_karet + cur_frm.doc.total_berat_batu);
    cur_frm.doc.total_berat_lilin = berat_lilin;
    refresh_field("total_berat_lilin");
    cur_frm.doc.tabel_detail[0].berat_lilin = berat_lilin;
    cur_frm.doc.tabel_detail[0].berat_pohon = cur_frm.doc.total_berat_pohon_lilin;
    refresh_field("tabel_detail");
  },
});
