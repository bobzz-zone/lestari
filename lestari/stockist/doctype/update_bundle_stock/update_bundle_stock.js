// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

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
	console.log("Connected");
	cur_frm.set_value("status_timbangan","Connected")
	cur_frm.refresh_field("status_timbangan");
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
async function disconnect() {
	try {
	  if (port) {
		await reader.cancel();
		console.log('Read operation has been canceled.');
		await reader.closed;
		console.log('Read stream has been closed.');
		await port.close();
		port = null;
		console.log('Serial port disconnected.');
	  } else {
		console.log('No serial port is connected.');
	  }
	} catch (error) {
	  console.error('Error:', error);
	}
  }

async function sendSerialLine() {
  dataToSend = "S";
  lineHistory.unshift(dataToSend);
  historyIndex = -1; // No history entry selected
  dataToSend = dataToSend + "\r\n";
  // appendToTerminal("> " + dataToSend);
  await writer.write(dataToSend);
}

async function appendToTerminal(newStuff) {
  // newStuff = newStuff.match(/[0-9]*[.]*[0-9]+\w/g);
  // newStuff = newStuff.match(/([0-9]*[.])\w+/s);
  // cur_frm.set_value("berat", flt(newStuff));
  // const valueString = new TextDecoder().decode(value);
  // const filteredValue = newStuff.match(/[-+]?0*(\.\d+)/g).map(x => x.replace(/^[-+]?0*([^0]+)/g, "$1")).join('');
  //   newStuff = newStuff.replace(/ST,\+0*([0-9]+\.[0-9]+)[A-Za-z]*/g, "").trim(); //timbangan suncho dan metler 
  newStuff = newStuff.replace(/[A-Z]|[a-z]/g, "").trim(); //timbangan suncho dan metler yang bener
  newStuff = parseFloat(newStuff)
//   let formattedValue = newStuff.replace(".", ",");

	//and
	// const text = newStuff;
	// const pattern = /ST,\+0*([0-9]+\.[0-9]+)[A-Za-z]*/g;
	// const matches = text.match(pattern);

	// // if (matches) {
	// const angka = matches[0].match(/[0-9]+\.[0-9]+/)[0];
	// console.log(parseFloat(angka)); // Output: 17.66
	// console.log(newStuff)
	// cur_frm.set_value("berat", angka);
	// cur_frm.refresh_field("berat");
	// }
  // newStuff = newStuff.replace(/[^\d.]/g, "").trim(); //timbangan AND
}

function hitung(){
	var totalberat = 0,
  	totaltransfer = 0;
	$.each(cur_frm.doc.items, function(i,e){
		// console.log(e.qty_penambahan)
		if(e.qty_penambahan != null){
		totalberat = parseFloat(totalberat) + parseFloat(e.qty_penambahan)
		console.log(totalberat)
		}
	})
	cur_frm.set_value("total_bruto", totalberat)
	cur_frm.refresh_field("total_bruto")

	cur_frm.clear_table("per_kadar")
		cur_frm.refresh_field('per_kadar');
		var totals = {};
			cur_frm.doc.items.forEach(function(row) {
				var kadar = row.kadar;
				var berat = parseFloat(row.qty_penambahan);
				var berat_transfer = parseFloat(row.berat_transfer);
				if (!totals[kadar]) {
					totals[kadar] = 0;
				}
				totals[kadar] += berat;
			});
			for (var kadar in totals) {
				var total_berat = totals[kadar];
				var child = cur_frm.add_child('per_kadar');
				child.kadar = kadar;
				child.bruto = total_berat;
				console.log(total_berat);
			}
			cur_frm.refresh_field('per_kadar');
}
var list_kat = [];
frappe.ui.form.on('Update Bundle Stock', {
	refresh: function(frm) {
		cur_frm.get_field("bundle").set_focus()
		frm.add_custom_button(__("Connect"), () => frm.events.get_connect(frm));
		// frm.add_custom_button(__("Disconnect"), () => frm.events.get_disconnect(frm));
		frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name","id_employee"]).then(function (responseJSON) {
		  cur_frm.set_value("pic", responseJSON.message.name);
		  cur_frm.set_value("id_employee", responseJSON.message.id_employee);
		  cur_frm.get_field("bundle").set_focus()
		  cur_frm.refresh_field("pic");
		  cur_frm.refresh_field("id_employee");
		//   console.log(responseJSON)
		})
		
		frm.set_query("pic", function(){
			return {
				"filters": [
					["Employee", "department", "=", "Stockist - LMS"],
				]
			}
		});
		// frm.set_query("sub_kategori","items", function(){
		// 	return {
		// 		"filters": [
		// 			["Item Group", "parent_item_group", "=", "Products"],
		// 		]
		// 	}
		// });
		frappe.db.get_list('Item Group', {
			filters: {
				parent_item_group: 'Products'
			}
		}).then(records => {
			for(var i = 0; i<= records.length; i++){
				list_kat.push(records[i].name)
			}
		})
		frm.set_query("sub_kategori", "items", function () {
			return {
				"filters": [
					["Item Group", "parent_item_group", "in", list_kat],
				]
			};
		  });
		frm.set_query("bundle", function(){
			return {
				"filters": [
					["Sales Stock Bundle", "aktif", "=", 1],
					["Sales Stock Bundle", "docstatus", "=", 1],
				]
			}
		});
		
	},
	total_perkadar:function(frm){
		hitung()
	},
	get_disconnect: function(frm){
		disconnect()
	},
	get_connect: function(frm){
		// frappe.msgprint("Connect");
		window.checkPort = async function (fromWorker) {
			if ("serial" in navigator) {
			  var ports = await navigator.serial.getPorts();
			  if (ports.length == 0 || fromWorker) {
				console.log("Not Connected");
				cur_frm.set_value("status_timbangan","Not Connect")
				cur_frm.refresh_field("status_timbangan");
				frappe.confirm(
				  "Browser Belum Memiliki Ijin Akses Serial!, Ijinkan ?",
				  async function () {
					// Prompt user to select any serial port.
					port = await navigator.serial.requestPort();
					connectSerial();
				  },
				  function () {}
				);
			  } else {
				port = ports[0];
				connectSerial();
				console.log("Connected");
				cur_frm.set_value("status_timbangan","Connected")
				cur_frm.refresh_field("status_timbangan");
				// Prompt user to select any serial port.
			  }
			} else {
			  frappe.msgprint("Your browser does not support serial device connection. Please switch to a supported browser to connect to your weigh device");
			}
		  };
		  window.checkPort(false);
	},
	id_employee: function(frm){
		frappe.db.get_value("Employee", { "id_employee": cur_frm.doc.id_employee }, ["name","employee_name"]).then(function (responseJSON) {
			cur_frm.set_value("nama_stokist", responseJSON.message.employee_name);
			cur_frm.set_value("pic", responseJSON.message.name);
			cur_frm.get_field("bundle").set_focus()
			cur_frm.refresh_field("nama_stokist");
			cur_frm.refresh_field("pic");
	})
	},
	type: function(frm){
		// cur_frm.fields_dic['items'].grid.get_field("sub_kategori").set_focus()
	}
});
frappe.ui.form.on('Detail Penambahan Stock', {
	items_add: function (frm, cdt, cdn){
		var d = locals[cdt][cdn];
        var idx = d.idx;
        var prev_kadar = 0;
		$.each(frm.doc.items, function(i,g){
			if(g.kadar != null){
				prev_kadar = g.kadar;
			}else{
				g.kadar = prev_kadar
			}
			// cur_frm.get_field('items').grid.get_row(g.name).columns_list[3].df.read_only = 1;
			cur_frm.refresh_field("item")
		})
        // if (idx > 1) {
        //     var prev_child = locals[cdt][idx - 1];
		// 	console.log(prev_child)
        //     prev_kadar = prev_child.kadar;
        // }
        // frappe.model.set_value(cdt, cdn, 'kadar', prev_kadar);
		d.kadar = prev_kadar
        cur_frm.refresh_field('items');
		hitung()
		// hitung(frm, cdt, cdn)
		if(cur_frm.doc.status_timbangan == "Connected"){
		// 	d.set_df_property("qty_penambahan","read_only",1)
		}else{
		// 	d.set_df_property("qty_penambahan","read_only",0)
		// var df = frappe.meta.get_docfield("Attribute Shopee","qty_penambahan", cur_frm.doc.items[d.idx]['parent']);
		// df.read_only = 1;
		// cur_frm.refresh_fields('items');
		}
	},
	items_remove: function(frm,cdt,cdn){
		hitung()
	},
	// item: function(frm,cdt,cdn){
	// 	var d = locals[cdt][cdn];	
	// 	frappe.msgprint(d.idx)
	// },
	sub_kategori: function (doc,cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.kadar != null){
		frappe.call({
			method: 'lestari.stockist.doctype.update_bundle_stock.update_bundle_stock.get_sub_item',
			args: {
				'kadar': d.kadar,
				'sub_kategori': d.sub_kategori
			},
			callback: function(r) {
				if (!r.exc) {
					d.item = r.message[0][0]
					d.gold_selling_item = r.message[0][1]
					cur_frm.refresh_field("items")
				}
			}
		});
		}
	}, 
	kadar: function (doc,cdt, cdn){
		var d = locals[cdt][cdn];
		// console.log(cdt)
		// console.log(cdn)
		frappe.model.set_value(cdt, cdn, 'qty_penambahan', "read_only", true);
		if(d.sub_kategori != null){
		frappe.call({
			method: 'lestari.stockist.doctype.update_bundle_stock.update_bundle_stock.get_sub_item',
			args: {
				'kadar': d.kadar,
				'sub_kategori': d.sub_kategori
			},
			callback: function(r) {
				if (!r.exc) {
					d.item = r.message[0][0]
					d.gold_selling_item = r.message[0][1]
					cur_frm.doc.id_row = d.idx
					// cur_frm.get_field('items').grid.get_row(cdn).columns_list[3].df.read_only = 1;
					cur_frm.doc.field_row = "qty_penambahan"
					cur_frm.refresh_field("id_row")
					cur_frm.refresh_field("field_row")
					cur_frm.refresh_field("items")
					
				}
			}
		});
		}
	}, 
	qty_penambahan: function(frm,cdt,cdn){
		hitung()
	},
	timbang: function(frm,cdt,cdn){
		var d = locals[cdt][cdn];
		sendSerialLine().then(function(){
			frappe.model.set_value(cdt, cdn, 'qty_penambahan', cur_frm.doc.berat);
		})
	},
	timbang1: function(frm,cdt,cdn){
		var d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'berat_transfer', cur_frm.doc.berat);
	}
});
