// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Work Order Gips", {
  refresh: function (frm) {
    frm.events.make_custom_buttons(frm);
    if (!frm.doc.tabel_pohon) {
      var dummy = [
        {
          nomor_base_karet: "A014",
          ukuran_jenis_sprue: "Kecil",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "A027",
          ukuran_jenis_sprue: "Kecil",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "B030",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B080",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B103",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B126",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B127",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B135",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B192",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B449",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B463",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B502",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B571",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B743",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B745",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B748",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B807",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B895",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B896",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B902",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B908",
          ukuran_jenis_sprue: "Sedang",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "C047",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C076",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C332",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C389",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C405",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C444",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C453",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C482",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C499",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C559",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C583",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C584",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C642",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C713",
          ukuran_jenis_sprue: "Besar",
          kadar: "06K-300",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "A091",
          ukuran_jenis_sprue: "Kecil",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "B002",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B004",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B007",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B021",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B027",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B031",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B059",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B065",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B070",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B073",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B085",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B116",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B120",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B123",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B143",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B146",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B162",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B239",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B293",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B318",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B322",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B331",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B344",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B396",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B405",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B416",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B420",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B465",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B483",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B548",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B550",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B586",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B597",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B603",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B607",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B610",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B616",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B674",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B680",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B684",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B689",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B692",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B695",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B698",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B705",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B708",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B718",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B737",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B753",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B774",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B778",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B784",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B793",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B796",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B803",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B816",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B818",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B821",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B856",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B906",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B918",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B929",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B950",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B954",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B957",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B961",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B962",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B984",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "C018",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C028",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C064",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C085",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C098",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C099",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C137",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C158",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C172",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C179",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C185",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C221",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C227",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C248",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C260",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C273",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C318",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C321",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C327",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C331",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C336",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C339",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C387",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C424",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C428",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C437",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C460",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C507",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C510",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C551",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C556",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C567",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C582",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C588",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C589",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C635",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C665",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C701",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C706",
          ukuran_jenis_sprue: "Besar",
          kadar: "08K-375",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "A042",
          ukuran_jenis_sprue: "Kecil",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "A043",
          ukuran_jenis_sprue: "Kecil",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "B017",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B042",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B333",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B594",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B722",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B802",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B926",
          ukuran_jenis_sprue: "Sedang",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "C193",
          ukuran_jenis_sprue: "Besar",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C276",
          ukuran_jenis_sprue: "Besar",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C653",
          ukuran_jenis_sprue: "Besar",
          kadar: "08KP-375P",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "A058",
          ukuran_jenis_sprue: "Kecil",
          kadar: "10K-450",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "A101",
          ukuran_jenis_sprue: "Kecil",
          kadar: "10K-450",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "B098",
          ukuran_jenis_sprue: "Sedang",
          kadar: "10K-450",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B366",
          ukuran_jenis_sprue: "Sedang",
          kadar: "10K-450",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B880",
          ukuran_jenis_sprue: "Sedang",
          kadar: "10K-450",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "A060",
          ukuran_jenis_sprue: "Kecil",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "A095",
          ukuran_jenis_sprue: "Kecil",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "A098",
          ukuran_jenis_sprue: "Kecil",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "A103",
          ukuran_jenis_sprue: "Kecil",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Kecil",
        },
        {
          nomor_base_karet: "B047",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B175",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B503",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B505",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B615",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B709",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B772",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B786",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B794",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B801",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B907",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B910",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B922",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B948",
          ukuran_jenis_sprue: "Sedang",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "C001",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C014",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C036",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C139",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C151",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C168",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C222",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C263",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C303",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C393",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C456",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C485",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C634",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C699",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C700",
          ukuran_jenis_sprue: "Besar",
          kadar: "16K-700",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "B149",
          ukuran_jenis_sprue: "Sedang",
          kadar: "20K-875",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B728",
          ukuran_jenis_sprue: "Sedang",
          kadar: "20K-875",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "B729",
          ukuran_jenis_sprue: "Sedang",
          kadar: "20K-875",
          ukuran_base_karet: "MT-Base Karet Sedang",
        },
        {
          nomor_base_karet: "C024",
          ukuran_jenis_sprue: "Besar",
          kadar: "20K-875",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C269",
          ukuran_jenis_sprue: "Besar",
          kadar: "20K-875",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C398",
          ukuran_jenis_sprue: "Besar",
          kadar: "20K-875",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
        {
          nomor_base_karet: "C404",
          ukuran_jenis_sprue: "Besar",
          kadar: "20K-875",
          ukuran_base_karet: "MT-Base Karet Besar",
        },
      ];
      console.log(dummy);
      for (let i = 0; i < dummy.length; i++) {
        var addnew = frappe.model.add_child(cur_frm.doc, "Work Order Gips Pohon", "tabel_pohon");
        addnew.nomor_base_karet = dummy[i].nomor_base_karet;
        addnew.ukuran_jenis_sprue = dummy[i].ukuran_jenis_sprue;
        addnew.kadar = dummy[i].kadar;
        addnew.ukuran_base_karet = dummy[i].ukuran_base_karet;
        // addnew.pohon_id = "DPL202202" + parseInt(Math.floor(Math.random() * 10000) + 1);
      }
      cur_frm.refresh_fields();
    }
  },
  make_custom_buttons: function (frm) {
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button(__("Rencana Produk Harian"), () => frm.events.get_item_rph(frm), __("Get Items From"));
    }
    if (frm.doc.__islocal != 1) {
      frm.add_custom_button(__("Generate Form Gips"), () => frm.events.generate_form_gips(frm), __("Generate"));
      frm.add_custom_button(__("Generate Form Gips1"), () => frm.events.generate_form_gips1(frm), __("Generate"));
      frm.add_custom_button(__("Generate Peta Oven"), () => frm.events.generate_form_oven(frm), __("Generate"));
      frm.add_custom_button(__("Generate Peta Oven1"), () => frm.events.generate_form_oven1(frm), __("Generate"));
      frm.add_custom_button(__("Generate Work Order Cor"), () => frm.events.generate_work_order_cor(frm), __("Generate"));
      frm.add_custom_button(__("Generate Work Order Cor1"), () => frm.events.generate_work_order_cor1(frm), __("Generate"));
    }
  },
  get_item_rph: function (frm) {
    erpnext.utils.map_current_doc({
      method: "lestari.lestari.doctype.work_order_gips.work_order_gips.make_wo_gips",
      source_doctype: "RPH Gips",
      target: frm,
      setters: {
        employee_id: frm.doc.employee_id || undefined,
      },
      get_query_filters: {
        docstatus: 1,
      },
    });
  },
  generate_work_order_cor: function (frm) {
    // frappe.msgprint("hallo");
    frappe.call({
      method: "lestari.lestari.doctype.work_order_gips.work_order_gips.generate_work_order_cor",
      args: {
        name: cur_frm.doc.name,
      },
      callback: function (r) {
        cur_frm.refresh_fields();
        if (!r.exc) {
          // code snippet
        }
      },
    });
  },
  generate_work_order_cor1: function (frm) {
    frm.call("generate_work_order_cor1", {});
  },
  generate_form_gips: function (frm) {
    frappe.call({
      method: "lestari.lestari.doctype.work_order_gips.work_order_gips.generate_form_gips",
      args: {
        name: cur_frm.doc.name,
      },
      callback: function (r) {
        cur_frm.refresh_fields();
        if (!r.exc) {
          // code snippet
        }
      },
    });
  },
  generate_form_gips1: function (frm) {
    frm.call("generate_form_gips1", {});
  },
  generate_form_oven: function (frm) {
    frappe.msgprint("hallo");
    frappe.call({
      method: "lestari.lestari.doctype.work_order_gips.work_order_gips.generate_form_oven",
      args: {
        name: cur_frm.doc.name,
      },
      callback: function (r) {
        cur_frm.refresh_fields();
        if (!r.exc) {
          // code snippet
        }
      },
    });
  },
  generate_form_oven1: function (frm) {
    frm.call("generate_form_oven1", {});
  },
  mesin_gips_option: function (frm) {
    var total_spk_gips = cur_frm.doc.tabel_pohon.length;
    frappe.db
      .get_list("Data Mesin Gips Batch", {
        filters: {
          parent: cur_frm.doc.mesin_gips_option,
          total_spk_gips: total_spk_gips,
          standart: 1,
        },
        fields: ["total_spk_gips", "jumlah_batch", "standart"],
      })
      .then((batch) => {
        var addnew = frappe.model.add_child(cur_frm.doc, "Work Order Gips Mesin", "tabel_mesin");
        addnew.mesin_gips = cur_frm.doc.mesin_gips_option;
        addnew.total_spk_gips = batch[0].total_spk_gips;
        addnew.pohon_per_batch = parseInt(cur_frm.doc.data_ukuran_mesin);
        addnew.jumlah_batch = batch[0].jumlah_batch;
        addnew.total_per_batch = parseInt(cur_frm.doc.data_ukuran_mesin) * parseInt(batch[0].jumlah_batch);
        addnew.standart = batch[0].standart;
        cur_frm.refresh_fields();
      });
  },
  // jenis_gips: function (frm) {
  //   frappe.msgprint(cur_frm.doc.jenis_gips);
  //   if (cur_frm.doc.__islocal == 1) {
  //     frappe.throw("Silahkan Simpan Document Terlebih Dahulu");
  //   } else if (cur_frm.doc.jenis_gips && !cur_frm.doc.__islocal) {
  //     frappe.call({
  //       method: "lestari.lestari.doctype.work_order_gips.work_order_gips.generate_jenis_gips",
  //       args: {
  //         name: cur_frm.doc.name,
  //         jenis_gips: cur_frm.doc.jenis_gips,
  //       },
  //       callback: function (r) {
  //         // cur_frm.refresh_fields();
  //         if (!r.exc) {
  //           // code snippet
  //           cur_frm.refresh_fields();
  //           // var doc = frappe.model.sync(r.message);
  //           // frappe.set_route("Form", r.message.doctype, r.message.name);
  //         }
  //       },
  //     });
  //   } else {
  //     frappe.throw("Silahkan Pilih Jenis Gips Terlebih Dahulu");
  //   }
  // },
  jenis_gips: function (frm) {
    frappe.msgprint(cur_frm.doc.jenis_gips);
    if (cur_frm.doc.__islocal == 1) {
      frappe.throw("Silahkan Simpan Document Terlebih Dahulu");
    } else if (cur_frm.doc.jenis_gips && !cur_frm.doc.__islocal) {
      frm.call("generate_jenis_gips1", {});
    } else {
      frappe.throw("Silahkan Pilih Jenis Gips Terlebih Dahulu");
    }
  },
  mesin_gips: function (frm) {
    frappe.call({
      method: "lestari.lestari.doctype.work_order_gips.work_order_gips.kapasitas_mesin_gips",
      args: {
        mesin_gips: cur_frm.doc.mesin_gips,
      },
      callback: function (r) {
        if (!r.exc) {
          console.log(r);
          cur_frm.doc.kapasitas_mesin = r.message.kapasitas_mesin;
          cur_frm.doc.ukuran_mesin = r.message.ukuran_mesin;
          cur_frm.refresh_fields();
        }
      },
    });
  },
  generate_mesin: function (frm) {
    if (frm.is_dirty()) {
      frappe.show_alert("Save Document Terlebih dahulu!!");
    } else {
      frappe.call({
        method: "lestari.lestari.doctype.work_order_gips.work_order_gips.generate_mesin",
        args: {
          name: cur_frm.doc.name,
        },
        callback: function (r) {
          if (!r.exc) {
            console.log(r);
            cur_frm.refresh_fields();
            // cur_frm.doc.kapasitas_mesin = r.message.kapasitas_mesin;
            // cur_frm.doc.ukuran_mesin = r.message.ukuran_mesin;
            // cur_frm.refresh_fields();
          }
        },
      });
    }
  },
  simpan: function (frm) {
    if (!cur_frm.doc.mesin_gips) {
      frappe.msgprint("Pilih Mesin Gips Terlebih Dahulu");
    } else {
      var pohon = cur_frm.doc.tabel_pohon;
      var kapasitas_mesin = cur_frm.doc.kapasitas_mesin;
      var ukuran_mesin = cur_frm.doc.ukuran_mesin;
      var sub_total_berat = 0;
      var pilih = 0;

      for (let i = 0; i < pohon.length; i++) {
        if (pohon[i].__checked == 1) {
          if (!pohon[i].mesin_gips) {
            sub_total_berat = sub_total_berat + pohon[i].sub_total_berat;
            pilih++;
          } else {
            frappe.throw("Pohon yang anda pilih sudah ada di Tabel Batch");
          }
        }
      }
      console.log(sub_total_berat);
      if (pilih == ukuran_mesin) {
        if (sub_total_berat < kapasitas_mesin) {
          console.log("ini adalah untuk pilih Pohon");
          pindah();
          frappe.msgprint("Pohon Sukses dipilih!!");
        } else {
          frappe.throw("Pastikan Jumlah yang dipilih sama dengan Kapasitas Mesin");
        }
      } else {
        console.log("Pastikan Jumlah yang dipilih sama dengan Ukuran Mesin");
      }
      console.log(sub_total_berat);
    }
  },
});

function pindah() {
  var pohon = cur_frm.doc.tabel_pohon;
  var tot_batch = cur_frm.doc.total_batch + 1;
  for (let i = 0; i < pohon.length; i++) {
    if (pohon[i].__checked == 1) {
      var addnew = frappe.model.add_child(cur_frm.doc, "Work Order Gips Batch", "tabel_batch");
      addnew.nomor_base_karet = pohon[i].nomor_base_karet;
      addnew.kadar = pohon[i].kadar;
      addnew.ukuran_base_karet = pohon[i].ukuran_base_karet;
      addnew.mesin_gips = cur_frm.doc.mesin_gips;
      addnew.no_batch_gips = tot_batch;
      pohon[i].__checked = 0;
      pohon[i].mesin_gips = cur_frm.doc.mesin_gips;
    }
  }
  cur_frm.set_value("total_batch", tot_batch);
  cur_frm.refresh_fields();
}
// frappe.ui.form.on("Work Order Gips Pohon", {
//   pohon_id: function (doc, cdt, cdn) {
//     var d = locals[cdt][cdn];
//     d.barcode = d.pohon_id;
//     refresh_field("tabel_pohon");
//   },
// });
