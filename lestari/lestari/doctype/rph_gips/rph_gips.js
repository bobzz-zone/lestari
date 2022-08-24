// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt
frappe.ui.form.on("RPH Gips", {
  refresh: function (frm) {
    frm.events.make_custom_buttons(frm);
  },
  make_custom_buttons: function (frm) {
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(__("Ambil NTHKO Lilin"), () => frm.events.get_items_nthko_lilin(frm));
    }
  },
  get_items_nthko_lilin: async function (frm) {
    var d = await erpnext.utils.map_current_doc({
      method: "lestari.lestari.doctype.rph_gips.rph_gips.get_items_nthko_lilin",
      source_doctype: "NTHKO Lilin",
      target: frm,
      size: "extra-large",
      setters: {
        pohon_id: frm.doc.pohon_id || undefined,
        nomor_base_karet: frm.doc.nomor_base_karet || undefined,
      },
      get_query_filters: {
        docstatus: 1,
      },
    });
    // console.log($(document).find(".modal-dialog"));
    // console.log(d.$wrapper);
    // cur_frm.refresh_fields();
    // $(document).find(".modal-dialog").attr("style", "max-width:1000px !important");
    // d.$wrapper.dialog.$wrapper.find(".modal-dialog").css("max-width", "875px");
    // d.$wrapper.css("max-width", "90%");
    // d.$wrapper.css("width", "90%");
  },
  get_data: function (frm) {
    frappe.call({
      method: "lestari.lestari.doctype.rencana_produk_harian.rencana_produk_harian.get_data_gips",
      args: {
        from_tanggal: cur_frm.doc.from_tanggal,
        to_tanggal: cur_frm.doc.to_tanggal,
        kadar: cur_frm.doc.kadar,
        ukuran_base_karet: cur_frm.doc.ukuran_base_karet,
      },
      callback: function (r) {
        var data = r.message;
        console.log(data);
        if (!r.exc) {
          for (let i = 0; i < data.length; i++) {
            var addnew = frappe.model.add_child(cur_frm.doc, "RPH Gips Detail", "tabel_gips");
            addnew.no_spk = data[i].no_spk;
            addnew.no_pohon = data[i].no_pohon;
            addnew.tanggal_pohonan = data[i].tanggal_pohonan;
            addnew.pohon_id = data[i].pohon_id;
            addnew.kadar = data[i].kadar;
            addnew.qty = data[i].qty;
            addnew.ukuran = data[i].ukuran;
            addnew.ukuran_base_karet = data[i].ukuran_base_karet;
            addnew.berat_lilin = data[i].berat_lilin;
            addnew.berat_batu = data[i].berat_batu;
            addnew.berat_pohon = data[i].berat_pohon;
          }
          cur_frm.refresh_fields();
        }
      },
    });
  },
});
