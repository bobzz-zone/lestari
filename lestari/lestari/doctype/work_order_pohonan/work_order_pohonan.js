// Copyright (c) 2021, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Work Order Pohonan", {
  setup: function (frm) {
    frm.set_query("tools", "mul_id", function (doc, cdt, cdn) {
      //   var d = locals[cdt][cdn];
      //
      //   };
      // });
      frappe.db.get_list("Data Pohon Lilin Resep", { filters: { parent: cur_frm.doc.pohon_id }, fields: ["resep_cetakan", "rubber_mould"] }).then((resep) => {
        for (let i = 0; i < resep.length; i++) {
          return {
            filters: {
              item_code: resep[i].rubber_mould,
            },
          };
        }
      });
    });
  },
  refresh: function (frm) {
    frm.add_custom_button(__("Make Stock Entry"), () =>
      frappe.call({
        method: "lestari.lestari.doctype.work_order_pohonan.work_order_pohonan.make_stock_entry",
        args: {
          no_dpl: cur_frm.doc.pohon_id,
          no_ppl: cur_frm.doc.name,
          //   status: cur_frm.doc.status,
        },
        callback: function (r) {
          if (!r.exc) {
            var doc = frappe.model.sync(r.message);
            frappe.set_route("Form", r.message.doctype, r.message.name);
          }
        },
      })
    );
  },
});
