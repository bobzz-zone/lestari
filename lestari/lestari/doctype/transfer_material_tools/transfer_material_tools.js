// Copyright (c) 2021, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transfer Material Tools", {
  // refresh: function(frm) {

  // }
  get_material: function (frm) {
    if (!frm.doc.item_group) {
      frappe.throw(__("To Get Material Recap, 'Fill Item Group And Item Group Material' field is mandatory"));
    }
    const set_fields = ["item", "item_name", "qty", "wo"];

    frappe.call({
      method: "lestari.lestari.doctype.transfer_material_tools.transfer_material_tools.get_material_recap",
      args: {
        item_group: cur_frm.doc.item_group_material,
      },
      callback: function (r) {
        console.log(r);
        if (r.message) {
          frm.set_value("materials", []);
          $.each(r.message, function (i, d) {
            var item = frm.add_child("materials");
            console.log(item);
            for (let key in d) {
              if (d[key] && in_list(set_fields, key)) {
                item[key] = d[key];
              }
            }
          });
        }
        refresh_field("materials");
      },
    });
    // } else {
    //   const title = __("Material Recap For Item Group {0}", [frm.doc.item_group]);
    //   var dialog = new frappe.ui.Dialog({
    //     title: title,
    //     fields: [
    //       {
    //         label: __("Item Group"),
    //         fieldtype: "Link",
    //         fieldname: "item_group",
    //         read_only: true,
    //         default: frm.doc.item_group,
    //       },
    //       {
    //         label: __("Item Group Material (Optional)"),
    //         fieldtype: "Table MultiSelect",
    //         fieldname: "item_groups",
    //         options: "Transfer Material Tool Item Group",
    //         description: __("Optional"),
    //         get_query: function () {
    //           return {
    //             filters: {
    //               parent_item_group: frm.doc.item_group,
    //             },
    //           };
    //         },
    //       },
    //     ],
    //   });

    //   dialog.show();

    //   dialog.set_primary_action(__("Get Material"), () => {
    //     let item_groups = dialog.get_values().item_groups;
    //     frm.events.get_items_for_material_recap(frm, item_groups);
    //     dialog.hide();
    //   });
  },
});
