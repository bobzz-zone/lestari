// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txtif (!window.created_date) {
var port,
  textEncoder,
  writableStreamClosed,
  writer,
  dataToSend,
  historyIndex = -1;
const lineHistory = [];
const baud = 9800;

async function connectSerial() {
  try {
    // await port.open({ baudRate: document.getElementById("baud").value });
    await port.open({ baudRate: 9600 });
    listenToPort();

    textEncoder = new TextEncoderStream();
    writableStreamClosed = textEncoder.readable.pipeTo(port.writable);

    writer = textEncoder.writable.getWriter();
  } catch {
    alert("Serial Connection Failed");
  }
}
async function listenToPort() {
  const textDecoder = new TextDecoderStream();
  const readableStreamClosed = port.readable.pipeTo(textDecoder.writable);
  const reader = textDecoder.readable.getReader();

  // console.table(textDecoder);
  // console.table(readableStreamClosed);
  // console.table(reader);

  // Listen to data coming from the serial device.
  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      // Allow the serial port to be closed later.
      //reader.releaseLock();
      break;
    }
    // value is a string.
    //   document.getElementById("lineToSend").value = value;
    console.log("value:" + value);
    // cur_frm.set_value("berat", value);
    // cur_frm.refresh_field("berat");
    appendToTerminal(value);
  }
}
async function sendSerialLine() {
  dataToSend = "S";
  lineHistory.unshift(dataToSend);
  historyIndex = -1; // No history entry selected
  dataToSend = dataToSend + "\r\n";
  // appendToTerminal("> " + dataToSend);
  await writer.write(dataToSend);
  // cur_frm.set_value("kirim_serial", "");
  //await writer.releaseLock();
}
// const serialResultsDiv = cur_frm.doc.berat;

async function appendToTerminal(newStuff) {
  // newStuff = newStuff.match(/[0-9]*[.]*[0-9]+\w/g);
  // newStuff = newStuff.match(/([0-9]*[.])\w+/s);
  cur_frm.set_value("berat", flt(newStuff));
  // newStuff = newStuff.replace(/[A-Z]|[a-z]/g, "").trim();/ timbangan suncho dan metler
  newStuff = newStuff.replace(/[^\d.]/g, "").trim(); //timbangan AND
  cur_frm.set_value("berat_1", newStuff);
  // frappe.msgprint(newStuff);
}
frappe.ui.form.on("Form Berat Material Pohon", {
  onload: function (frm) {
    window.checkPort = async function (fromWorker) {
      if ("serial" in navigator) {
        var ports = await navigator.serial.getPorts();
        if (ports.length == 0 || fromWorker) {
          frappe.confirm(
            "Please provide permission to connect to the weigh device",
            async function () {
              // Prompt user to select any serial port.
              port = await navigator.serial.requestPort();

              connectSerial();
              // ports = await navigator.serial.requestPort();
              //Call connect again if the worker is already initialized
              // if (typeof window.mettlerWorker != "undefined") {
              //   window.mettlerWorker.postMessage({ command: "connect" });
              // }
            },
            function () {}
          );
        } else {
          port = ports[0];
          connectSerial();
          // Prompt user to select any serial port.
        }
      } else {
        frappe.msgprint("Your browser does not support serial device connection. Please switch to a supported browser to connect to your weigh device");
      }
    };
    window.checkPort(false);
  },
  refresh: function (frm) {},
  timbang: function (frm) {
    sendSerialLine();
  },
  connect: function (frm) {
    connectSerial();
  },
  kirim: function (frm) {
    sendSerialLine();
  },
  // after_save: function (frm) {
  //   frappe.db.get_doc("Work Order Pohonan", frm.doc.wo_id).then((r) => {
  //     console.log(r);
  //     frappe.set_route("Form", r.message.doctype, r.message.name);
  //   });
  // },
  //     frappe.call({
  //       method: "lestari.lestari.doctype.form_berat_material_pohon.form_berat_material_pohon.get_fbmp",
  //       args: {
  //         no_fbmp: cur_frm.doc.name,
  //         no_wo: cur_frm.doc.wo_id,
  //       },
  //       callback: function (r) {
  //         if (!r.exc) {
  //           var doc = frappe.model.sync(r.message);
  //           frappe.set_route("Form", r.message.doctype, r.message.name);
  //         }
  //       },
  //     });
  //   },
});
frappe.ui.form.on("Form Berat Material Batu", {
  berat: function (doc, cdn, cdt) {
    var d = locals[cdn][cdt];
    cur_frm.doc.total_berat_batu += d.berat;
    refresh_field("total_berat_batu");
  },
});
