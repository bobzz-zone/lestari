// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

// imported_helper(args);
// var printmgr = undefined;
// //Check printmgr WebSocket status
// function jspmWSStatus() {
//   if (JSPM.JSPrintManager.websocket_status == JSPM.WSStatus.Open) return true;
//   else if (JSPM.JSPrintManager.websocket_status == JSPM.WSStatus.Closed) {
//     alert("JSPrintManager (JSPM) is not installed or not running! Download JSPM Client App from https://neodynamic.com/downloads/jspm");
//     return false;
//   } else if (JSPM.JSPrintManager.websocket_status == JSPM.WSStatus.Blocked) {
//     alert("JSPM has blocked this website!");
//     return false;
//   }
// }

frappe.ui.form.on("NTHKO Lilin", {
  // setup: function (fmr) {
  //   frappe.require("assets/lestari/js/JSPrintManager/JSPrintManager.js", function () {
  //     //   console.log(printmgr);
  //     JSPM.JSPrintManager.auto_reconnect = true;
  //     JSPM.JSPrintManager.start();
  //     JSPM.JSPrintManager.WS.onStatusChanged = function () {
  //       if (jspmWSStatus()) {
  //         //get client installed printers
  //         JSPM.JSPrintManager.getPrinters().then(function (myPrinters) {
  //           var options = "";
  //           for (var i = 0; i < myPrinters.length; i++) {
  //             options += "<option>" + myPrinters[i] + "</option>";
  //             console.log(myPrinters[i]);
  //           }
  //           $("select[data-fieldname='installedprintername']").html(options);
  //         });
  //       }
  //     };
  //   });
  // },
  refresh: function (frm) {
    //WebSocket settings
    // console.log(printmgr);

    frm.events.make_custom_buttons(frm);
  },
  make_custom_buttons: function (frm) {
    // if (frm.doc.docstatus === 0) {
    frm.add_custom_button("PRINT THERMAL", () => {
      send2bridge(frm, "NTHKO Lilin", "THERMAL");
    });
    frm.add_custom_button("PRINT LASER", () => {
      send2bridge(frm, "NTHKO Lilin", "LASER");
    });
    // frm.add_custom_button(__("Print Laser"), () =>
    //   window.open("https://lms.digitalasiasolusindo.com/printview?doctype=NTHKO%20Lilin&name=NTHKO20221000001&trigger_print=1&format=NTHKO%20Lilin&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en", "_blank")
    // );
    // }
  },
  total_berat_pohon_lilin: function (frm) {
    var berat_lilin = 0;
    frappe.msgprint(this);
    berat_lilin = cur_frm.doc.total_berat_pohon_lilin - (cur_frm.doc.total_berat_base_karet + cur_frm.doc.total_berat_batu);
    cur_frm.doc.total_berat_lilin = berat_lilin;
    refresh_field("total_berat_lilin");
    cur_frm.doc.tabel_detail[0].berat_lilin = berat_lilin;
    cur_frm.doc.tabel_detail[0].berat_pohon = cur_frm.doc.total_berat_pohon_lilin;
    refresh_field("tabel_detail");
  },
  installedprintername: function (frm) {
    frappe.msgprint(frm.doc.installedprintername);
  },
});

var send2bridge = function (frm, print_format, print_type) {
  // initialice the web socket for the bridge
  var printService = new frappe.silent_print.WebSocketPrinter();
  console.log(printService);
  frappe.call({
    method: "silent_print.utils.print_format.create_pdf",
    args: {
      doctype: frm.doc.doctype,
      name: frm.doc.name,
      silent_print_format: print_format,
      no_letterhead: 1,
      _lang: "en",
    },
    callback: (r) => {
      printService.submit({
        type: print_type, //this is the label that identifies the printer in WHB's configuration
        url: "file.pdf",
        file_content: r.message.pdf_base64,
      });
    },
  });
};
