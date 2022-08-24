// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card Operator", {
  refresh: function (frm) {},
  // simpan_material: function (frm) {
  //   frappe.call({
  //     method: "lestari.lestari.doctype.job_card_operator.job_card_operator.simpan_material",
  //     args: {
  //       name: cur_frm.doc.name,
  //       no_pohon: cur_frm.doc.no_pohon,
  //     },
  //     callback: function (r) {
  //       if (!r.exc) {
  //         cur_frm.refresh_fields();
  //         // code snippet
  //       }
  //     },
  //   });
  // },
});
