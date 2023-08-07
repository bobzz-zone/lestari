// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("RPH Lilin", {
  setup: function (frm) {
    frappe.db.get_value("Employee", { user_id: frappe.session.user }, "name").then(function (responseJSON) {
      cur_frm.set_value("employee_id", responseJSON.message.name);
      cur_frm.refresh_field("employee_id");
    });
  },
  refresh: function (frm) {
    frm.events.make_custom_buttons(frm);
  },
  make_custom_buttons: function (frm) {
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(__("Ambil SPK Produksi"), () => frm.events.get_items_from_spk_produksi(frm));
    }
 },
get_items_from_spk_produksi: async function (frm, dialog) {
   var r =  await erpnext.utils.map_current_doc({

      method: "lestari.lestari.doctype.rph_lilin.rph_lilin.get_items_from_spk_produksi",
      source_doctype: "SPK Produksi",
      target: frm,
      setters: {
        area: undefined,
        tanggal_spk: undefined,
      },
      size: "extra-large",
      get_query_filters: {
        docstatus: 1,
        // status: ["not in", ["Cancel"]],
        company: frm.doc.company,
      },
      allow_child_item_selection: true,
      child_fieldname: "tabel_rencana_produksi",
      child_columns: ["produk_id", "kategori", "sub_kategori", "kadar", "qty"],
    });
    // r.dialog.hide();
    $(document).on("frappe.ui.Dialog:shown", function() {
        // Your custom logic here, e.g., perform some action when the dialog is shown
        if(!r.dialog.fields_dict['allow_child_item_selection'].get_value()){
            r.dialog.fields_dict.allow_child_item_selection.$input.click()
        }

        if($(":input[data-fieldname='allow_child_item_selection']").is(':checked')){
          setTimeout(function(){
            r.child_datatable.columnmanager.applyFilter(r.child_datatable.columnmanager.getAppliedFilters())
          }, 2000)
        }
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
