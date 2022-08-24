// Copyright (c) 2021, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Work Order Pohonan", {
  refresh: function (frm) {
    // get_mul(frm);
    frm.set_query("base_sprue_serial", function () {
      return {
        filters: {
          item_code: cur_frm.doc.set_sprue,
        },
      };
    });
    frm.set_query("mul_id", "tools", function (doc, cdt, cdn) {
      var d = locals[cdt][cdn];
      return {
        filters: {
          item_code: d.rubber_mould,
          warehouse: "Inventory - L",
        },
      };
    });
    frm.set_query("resep_mul_karet", "tools", function () {
      return {
        query: "lestari.lestari.doctype.work_order_pohonan.work_order_pohonan.get_resep",
        filters: {
          parent: frm.doc.pohon_id,
        },
      };
    });
    if (cur_frm.doc.workflow_state == "In Progress" && cur_frm.doc.docstatus == 0) {
      frm.add_custom_button(
        __("Stock Entry"),
        () =>
          frappe.call({
            method: "lestari.lestari.doctype.work_order_pohonan.work_order_pohonan.make_stock_entry",
            args: {
              no_dpl: cur_frm.doc.pohon_id,
              no_wop: cur_frm.doc.name,
              serial_sprue: cur_frm.doc.base_sprue_serial,
              status: cur_frm.doc.status_pohonan,
            },
            callback: function (r) {
              if (!r.exc) {
                var doc = frappe.model.sync(r.message);
                frappe.set_route("Form", r.message.doctype, r.message.name);
              }
            },
          }),
        "Buat"
      );
    }
    if (cur_frm.doc.workflow_state == "In Progress" && cur_frm.doc.docstatus == 0) {
      frm.add_custom_button(
        __("Berat Material"),
        () =>
          frappe.call({
            method: "lestari.lestari.doctype.work_order_pohonan.work_order_pohonan.berat_material",
            args: {
              no_dpl: cur_frm.doc.pohon_id,
              no_wop: cur_frm.doc.name,
              //   status: cur_frm.doc.status,
            },
            callback: function (r) {
              if (!r.exc) {
                var doc = frappe.model.sync(r.message);
                frappe.set_route("Form", r.message.doctype, r.message.name);
              }
            },
          }),
        "Buat"
      );
    }
    // frm.change_custom_button_type("Berat Material", "Make", "danger");
    // if (cur_frm.doc.workflow_state == "Finished" && cur_frm.doc.docstatus == 1) {
    //   frm.add_custom_button(__("Masukkan Berat Material"), () =>
    //     frappe.call({
    //       method: "lestari.lestari.doctype.work_order_pohonan.work_order_pohonan.berat_material",
    //       args: {
    //         no_dpl: cur_frm.doc.pohon_id,
    //         no_wop: cur_frm.doc.name,
    //         //   status: cur_frm.doc.status,
    //       },
    //       callback: function (r) {
    //         if (!r.exc) {
    //           var doc = frappe.model.sync(r.message);
    //           frappe.set_route("Form", r.message.doctype, r.message.name);
    //         }
    //       },
    //     })
    //   );
    // }
  },
});
// function get_mul(frm) {
//   frm.set_query("mul_id", "tools", function () {
//     // console.log(frm.doc.party)
//     var child_names = [];
//     if (frm.doc.resep) {
//       for (var i = 0; i < frm.doc.resep.length; i++) {
//         if (frm.doc.resep[i].rubber_mould) {
//           child_names.push(frm.doc.resep[i].rubber_mould);
//         }
//       }
//     }
//     return {
//       query: "lestari.lestari.doctype.work_order_pohonan.work_order_pohonan.get_mul",
//       filters: {
//         child_list: child_names,
//         dplname: frm.doc.pohon_id,
//       },
//     };
//   });
// }
