// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transfer Material", {
  refresh: function (frm) {
    frm.set_query("nthko_area", "transfer_detail", function (doc, cdn, cdt) {
      return {
        query: "lestari.lestari.doctype.transfer_material.transfer_material.get_nthko",
        filters: {
          module: "Lestari",
          is_submittable: "1",
          name: "%NTHKO%",
        },
      };
    });
  },
});
