// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rencana Produk Harian", {
  refresh: function (frm) {
    frm.set_value("from_tanggal", frappe.datetime.add_days(frappe.datetime.now_datetime(), -1));
    // frm.events.make_custom_buttons(frm);
    frm.set_query("kategori", function () {
      return {
        filters: {
          parent_item_group: "Products",
        },
      };
    });
    if (!cur_frm.doc.kategori) {
      frm.set_query("sub_kategori", function () {
        return {
          filters: {
            parent_item_group: cur_frm.doc.kategori,
          },
        };
      });
    }
  },
  area: function (frm) {
    frm.clear_custom_buttons();
    frm.events.make_custom_buttons(frm);
  },
  get_data: function (frm) {
    frappe.call({
      method: "lestari.lestari.doctype.rencana_produk_harian.rencana_produk_harian.get_data_gips",
      args: {
        from_tanggal: cur_frm.doc.from_tanggal,
        to_tanggal: cur_frm.doc.to_tanggal,
        kadar: cur_frm.doc.kadar,
        jenis_sprue: cur_frm.doc.jenis_sprue,
      },
      callback: function (r) {
        var data = r.message;
        console.log(data);
        if (!r.exc) {
          console.log(data["area"]);
          for (let i = 0; i < data.length; i++) {
            var addnew = frappe.model.add_child(cur_frm.doc, "Rencana Produk Harian Gips", "tabel_gips");
            addnew.no_spk = data[i].no_spk;
            addnew.no_pohon = data[i].no_pohon;
            addnew.tanggal_pohonan = data[i].tanggal_pohonan;
            addnew.pohon_id = data[i].pohon_id;
            addnew.kadar = data[i].kadar;
            addnew.qty = data[i].qty;
            addnew.ukuran = data[i].ukuran;
            addnew.jenis_sprue = data[i].jenis_sprue;
            addnew.berat_lilin = data[i].berat_lilin;
            addnew.berat_batu = data[i].berat_batu;
            addnew.berat_pohon = data[i].berat_pohon;
          }
          cur_frm.refresh_fields();
        }
      },
    });
  },
  make_custom_buttons: function (frm) {
    if (frm.doc.docstatus === 0 && frm.doc.area === "Lilin - L") {
      // frm.remove_custome_button("Form Hasil WO", "Get Item From");
      frm.add_custom_button(__("Material Request"), () => frm.events.get_items_from_material_request(frm), __("Get Items From"));
    }
    if (frm.doc.docstatus === 0 && frm.doc.area === "Lilin - L") {
      frm.add_custom_button(__("Sales Order"), () => frm.events.get_items_from_sales_order(frm), __("Get Items From"));
    }
    if (frm.doc.docstatus === 0 && frm.doc.area === "Lilin - L") {
      frm.add_custom_button(__("SPK Produksi"), () => frm.events.get_items_from_spk_produksi(frm), __("Get Items From"));
    }
    if (frm.doc.docstatus === 0 && frm.doc.area === "GCP - L") {
      frappe.msgprint("test");
      // frm.remove_custome_button(["Form Hasil WO", "Sales Order"], "Get Item From");
      frm.add_custom_button(__("Form Hasil WO"), () => frm.events.get_items_form_hasil_wo(frm), __("Get Items From"));
    }
  },
  get_items_from_spk_produksi: function (frm) {
    erpnext.utils.map_current_doc({
      method: "lestari.lestari.doctype.rencana_produk_harian.rencana_produk_harian.get_items_from_spk_produksi",
      source_doctype: "SPK Produksi",
      target: frm,
      setters: {
        // customer: frm.doc.customer || undefined,
        // no_spk: frm.doc.no_spk || undefined,
        // kadar: frm.doc.kadar || undefined,
        // produk_id: frm.doc.produk_id || undefined,
      },
      get_query_filters: {
        docstatus: 1,
        // status: ["not in", ["Cancel"]],
        company: frm.doc.company,
      },
    });
  },
  get_items_from_sales_order: function (frm) {
    erpnext.utils.map_current_doc({
      method: "lestari.lestari.doctype.rencana_produk_harian.rencana_produk_harian.make_material_request",
      source_doctype: "Sales Order",
      target: frm,
      setters: {
        customer: frm.doc.customer || undefined,
        delivery_date: undefined,
        currency: frm.doc.currency || undefined,
      },
      get_query_filters: {
        docstatus: 1,
        status: ["not in", ["Closed", "On Hold"]],
        per_delivered: ["<", 99.99],
        company: frm.doc.company,
      },
    });
  },
  get_items_from_material_request: function (frm) {
    erpnext.utils.map_current_doc({
      method: "lestari.lestari.doctype.rencana_produk_harian.rencana_produk_harian.get_material_request",
      source_doctype: "Material Request",
      target: frm,
      setters: {
        transaction_date: undefined,
        schedule_date: undefined,
        status: undefined,
      },
      get_query_filters: {
        docstatus: 1,
        status: ["!=", "Stopped"],
        per_ordered: ["<", 100],
        company: me.frm.doc.company,
      },
    });
  },
  get_items_form_hasil_wo: function (frm) {
    erpnext.utils.map_current_doc({
      method: "lestari.lestari.doctype.rencana_produk_harian.rencana_produk_harian.make_form_hasilwo",
      source_doctype: "Form Hasil Work Order",
      target: frm,
      setters: {
        pohon_id: frm.doc.pohon_id || undefined,
        base_sprue_serial: frm.doc.base_sprue_serial || undefined,
      },
      get_query_filters: {
        docstatus: 1,
      },
    });
    cur_frm.doc.area = "GCP - L";
    cur_frm.refresh_fields();
  },
});
