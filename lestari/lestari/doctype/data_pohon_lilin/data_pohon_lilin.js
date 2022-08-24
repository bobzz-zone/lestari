// Copyright (c) 2021, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Data Pohon Lilin", {
  // refresh: function (frm) {
  //   var workflow_state = cur_frm.doc.workflow_state;
  //   // if (cur_frm.doc.docstatus === 0 && cur_frm.doc.workflow_state === "Plan") {
  //   frm.add_custom_button(__("Work Order Pohonan"), () =>
    //   frappe.call({
    //     method: "lestari.lestari.doctype.data_pohon_lilin.data_pohon_lilin.make_proses_pohonan_lilin",
    //     args: {
    //       no_dpl: cur_frm.doc.name,
    //     },
    //     callback: function (r) {
    //       if (!r.exc) {
    //         var doc = frappe.model.sync(r.message);
    //         frappe.set_route("Form", r.message.doctype, r.message.name);
    //       }
    //     },
    //   })
    // );
  //   // }
  // },
  // get_data: function (frm) {
  //   frappe.msgprint("test");
  // },
  // make_journal_entry: function (frm) {
  //   frappe.model.open_mapped_doc({
  //     method: "lestari.lestari.doctype.data_pohon_lilin.data_pohon_lilin.make_stock_entry",
  //     frm: frm,
  //   });
  // },
  // get_rubber_mould: function (frm) {
  //   frappe.db.get_list("Data Pohon Lilin Resep", { filters: { parent: cur_frm.doc.name }, fields: ["resep_cetakan", "qty", "qty_mul"] }).then((resep) => {
  //     cur_frm.doc.serial = [];
  //     for (let i = 0; i < resep.length; i++) {
  //       var qty = resep[i].qty / resep[i].qty_mul;
  //       console.log("resep:" + resep[i].resep_cetakan + ", qty :" + qty);
  //       frappe
  //         .xcall("lestari.lestari.doctype.data_pohon_lilin.data_pohon_lilin.get_serial", {
  //           data_pohon: frm.doc.name,
  //           qty: resep[i].qty_mul,
  //           resep: resep[i].resep_cetakan,
  //         })
  //         .then((data) => {
  //           console.log(data);

  //           for (let j = 0; j < data.length; j++) {
  //             //frappe.msgprint(String(data[i].serial));
  //             var addnew = frappe.model.add_child(cur_frm.doc, "Data Pohon Lilin Serial", "serial");
  //             // addnew.serial = data[j].serial_name;
  //             addnew.qty = resep[i].qty / resep[i].qty_mul;
  //             addnew.rubber_mould = data[j].rubber_mould;
  //             addnew.resep = data[j].resep_cetakan;
  //             addnew.kode_perhiasan = data[j].kode_perhiasan;
  //             addnew.uom = data[j].stock_uom;
  //             // addnew.jumlah_pemakaian = 0;
  //             // addnew.status = data[j].status;
  //             // addnew.source_warehouse = data[j].warehouse;
  //           }
  //           cur_frm.refresh_fields();
  //           // frm.refresh_fields("serial");
  //         });
  //     }
  //   });
  // },
  // get_material: function (frm) {
  //   frappe
  //     .xcall("lestari.lestari.doctype.data_pohon_lilin.data_pohon_lilin.get_material", {
  //       data_pohon: frm.doc.name,
  //     })
  //     .then((data) => {
  //       console.log(data);
  //       cur_frm.doc.material = [];
  //       for (let i = 0; i < data.length; i++) {
  //         //frappe.msgprint(String(data[i].serial));
  //         var addnew = frappe.model.add_child(cur_frm.doc, "Data Pohon Lilin Material", "material");
  //         addnew.name1 = data[i].nama_batu;
  //         addnew.qty = data[i].qty;
  //         addnew.uom = data[i].uom;
  //       }
  //       cur_frm.refresh_fields();
  //       // frm.refresh_fields("serial");
  //     });
  // },
});
