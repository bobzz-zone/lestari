// Copyright (c) 2021, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Proses Pohonan Lilin", {
  refresh: function (frm) {
    if (cur_frm.doc.docstatus === 0 && cur_frm.doc.workflow_state !== "Pending") {
      if (cur_frm.doc.status === "Supermarket" || cur_frm.doc.status === "Gypsum" || cur_frm.doc.status === "Cor") {
        frm.add_custom_button(__("Make Stock Entry"), () =>
          frappe.call({
            method: "lestari.lestari.doctype.proses_pohonan_lilin.proses_pohonan_lilin.make_stock_entry",
            args: {
              no_dpl: cur_frm.doc.pohon_lilin,
              no_ppl: cur_frm.doc.name,
              status: cur_frm.doc.status,
            },
            callback: function (r) {
              if (!r.exc) {
                var doc = frappe.model.sync(r.message);
                frappe.set_route("Form", r.message.doctype, r.message.name);
              }
            },
          })
        );
      }
    }
    if (cur_frm.doc.docstatus === 1 && cur_frm.doc.status !== "Cor") {
      var label = "";
      if (cur_frm.doc.status === "Supermarket") {
        label = "Proses Pohonan Gypsum";
      }
      if (cur_frm.doc.status === "Gypsum") {
        label = "Proses Pohonan Oven";
      }
      if (cur_frm.doc.status === "Oven") {
        label = "Proses Pohonan Cor";
      }
      frm.add_custom_button(__(label), () =>
        frappe.call({
          method: "lestari.lestari.doctype.proses_pohonan_lilin.proses_pohonan_lilin.make_proses_pohonan_lilin",
          args: {
            no_dpl: cur_frm.doc.pohon_lilin,
            no_ppl: cur_frm.doc.name,
            status: cur_frm.doc.status,
          },
          callback: function (r) {
            if (!r.exc) {
              var doc = frappe.model.sync(r.message);
              console.log(r.message);
              frappe.set_route("Form", r.message.doctype, r.message.name);
            }
          },
        })
      );
    }
  },
  get_item: function (frm) {
    cur_frm.doc.serial = [];
    frappe
      .xcall("lestari.lestari.doctype.proses_pohonan_lilin.proses_pohonan_lilin.get_serial", {
        data_pohon: cur_frm.doc.pohon_lilin,
      })
      .then((data) => {
        for (let j = 0; j < data.length; j++) {
          var addnew = frappe.model.add_child(cur_frm.doc, "Proses Pohonan Lilin Serial", "rubber_mould");
          addnew.serial = data[j].serial;
          addnew.qty = 1;
          addnew.rubber_mould = data[j].rubber_mould;
          addnew.resep = data[j].resep_cetakan;
          addnew.kode_perhiasan = data[j].kode_perhiasan;
          addnew.uom = data[j].uom;
          addnew.jumlah_pemakaian = 0;
          addnew.status = data[j].status;
          addnew.source_warehouse = data[j].warehouse;
        }
        cur_frm.refresh_fields();
      });
    cur_frm.doc.material = [];
    frappe
      .xcall("lestari.lestari.doctype.proses_pohonan_lilin.proses_pohonan_lilin.get_material", {
        data_pohon: cur_frm.doc.pohon_lilin,
      })
      .then((data) => {
        for (let j = 0; j < data.length; j++) {
          var addnew = frappe.model.add_child(cur_frm.doc, "Proses Pohonan Lilin Material", "material");
          addnew.name1 = data[j].nama_batu;
          addnew.qty = data[j].qty;
          addnew.uom = data[j].uom;
        }
        cur_frm.refresh_fields();
      });
  },
});
