// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Work Order Cor", {
  refresh: function (frm) {
    frm.set_query("no_material_request", function () {
      return {
        filters: {
          work_order_cor: cur_frm.doc.name,
        },
      };
    });
    frm.set_query("material_cor", function () {
      return {
        query: "lestari.lestari.doctype.work_order_cor.work_order_cor.get_item_mr",
        filters: {
          parent: cur_frm.doc.no_material_request,
        },
      };
    });
    frm.set_query("pohon_id", function () {
      return {
        filters: {
          warehouse: "Gips - L",
        },
      };
    });
  },
  material_cor: function (frm) {
    console.log(cur_frm.doc.material_cor);
    frappe.db.get_value("Material Request Item", { filters: { parent: cur_frm.doc.material_corame }, fields: ["item_code"] }).then((item) => {
      console.log(item);
      cur_frm.set_value("material", item.item_code);
      cur_frm.refresh_field("material");
    });
  },
});
function get_item_mr_name(parent) {
  var child_names = [];
  frappe.db.get_list("Material Request Item", { filters: { parent: parent }, fields: ["name"] }).then((item) => {
    console.log(item);
    for (let i = 0; i < item.length; i++) {
      child_names.push(item.name);
    }
  });
  return child_names;
}
