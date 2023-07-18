// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

var port,
  textEncoder,
  writableStreamClosed,
  writer,
  dataToSend,
  historyIndex = -1,
  timbangan,
  type_timbangan = "AND",
  connected = 0;
const lineHistory = [];
const baud = 9800;

async function connectSerial() {
  try {
	// console.log("Connected");
	connected = 1;
	cur_frm.set_value("status_timbangan","Connected")
	cur_frm.refresh_field("status_timbangan");
    await port.open({ baudRate: 9600 });
    listenToPort();

    textEncoder = new TextEncoderStream();
    writableStreamClosed = textEncoder.readable.pipeTo(port.writable);

    writer = textEncoder.writable.getWriter();
	// await writer.write("S"+"\r\n");
	if(timbangan == null){
		timbangan = 1;
	}
	if(cur_frm.doc.berat==null && timbangan == 1){
	setInterval(function() {
		sendSerialLine()
	  }, 2500);
	}
  } catch {
    // alert("Serial Connection Failed");
  }
}
async function listenToPort() {
  const textDecoder = new TextDecoderStream();
  const readableStreamClosed = port.readable.pipeTo(textDecoder.writable);
  const reader = textDecoder.readable.getReader();
  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    // console.log("value:" + value);
    appendToTerminal(value);
  }
}
async function sendSerialLine() {
  if(type_timbangan == "AND"){
  dataToSend = "S";
  }else{
  dataToSend = "O9";
  }
  lineHistory.unshift(dataToSend);
  historyIndex = -1; // No history entry selected
  dataToSend = dataToSend + "\r\n";
  await writer.write(dataToSend);
}

async function appendToTerminal(newStuff) {
//   console.log("Timbangan"+timbangan)
//   console.log("newStuff"+newStuff)
  if (newStuff == "E01" || newStuff == "E" || newStuff == "01" && type_timbangan == "AND"){
	timbangan = 0;
	type_timbangan = "SHINKO";
  }
  // mettler
  newStuff = newStuff.replace("S S       ", "");
  newStuff = newStuff.replace("S       ", "");
  newStuff = newStuff.replace(" g", "");
  newStuff = newStuff.replace(" ", "");

  // // and 
  newStuff = newStuff.replace("ST,+0000", "");
  newStuff = newStuff.replace("ST,+000", "");
  newStuff = newStuff.replace("ST,+00", "");
  newStuff = newStuff.replace("ST,+0", "");
  newStuff = newStuff.replace("T,+0000", "");
  newStuff = newStuff.replace("T,+000", "");
  newStuff = newStuff.replace("T,+00", "");
  newStuff = newStuff.replace("T,+0", "");

  // shinko
  newStuff = newStuff.replace("+00000", "");
  newStuff = newStuff.replace("+0000", "");
  newStuff = newStuff.replace("+000", "");
  newStuff = newStuff.replace("+00", "");
  newStuff = newStuff.replace("+0", "");
  newStuff = newStuff.replace("+", "");

  // vibra
  newStuff = newStuff.replace("0000", "");
  newStuff = newStuff.replace("000", "");
  newStuff = newStuff.replace("00", "");
  if (newStuff.charAt(0) === '.') { // periksa apakah karakter pertama adalah titik
	  newStuff = newStuff.replace(/^\./, '0.'); // ganti karakter pertama dari titik menjadi 0.
  }
  if (newStuff.endsWith('.')) { // periksa apakah karakter terakhir adalah titik
	  newStuff += '00'; // tambahkan string "00" di belakangnya
  }
  if( connected == 1){
	  // var warna;
	  // frappe.call({
		  // 	method: 'frappe.client.get',
		  // 	args: {
			  // 	  doctype: 'User',
			  // 	  filters: { name: frappe.session.user },
			  // 	  fields: ['desk_theme'],
			  // 	},
			  // 	callback: function(response) {
				  // 	  var user = response.message;
				  // 	  var isDarkMode = user.desk_theme === 'Light';
				  
				  // 	  if (isDarkMode) {
					  // 		console.log("Mode Gelap aktif");
					  // 		warna = "#f9fafa"
					  // 	  } else {
						  // 		console.log("Mode Terang aktif");
						  // 		warna = "#1f272e"
						  // 	  }
						  // 	}
						  //   });	  
	let result = newStuff.includes("G S");
	if (result) {
		newStuff = newStuff.replace("G S", "");
		// cur_frm.set_value("berat", newStuff);
		// cur_frm.refresh_field("berat");
	}
	cur_frm.set_value("berat", newStuff);
	cur_frm.refresh_field("berat");
	$(".berat_real").text(cur_frm.doc.berat);
  }
}
/////////////////////////////////////////////////////////
// 	if (timbangan == 1){
// 	const text = newStuff;
// 	const pattern = /ST,\+0*([0-9]+\.[0-9]+)[A-Za-z]*/g;
// 	const matches = text.match(pattern);
// 	const angka = matches[0].match(/[0-9]+\.[0-9]+/)[0];
// 	}else{
// 		newStuff = newStuff.replace(/[A-Z]|[a-z]/g, "").trim(); //timbangan suncho dan metler yang bener
//   		angka = parseFloat(newStuff)
// 	}
// 	console.log(parseFloat(angka)); // Output: 17.66
// 	if (angka != null){
// 		timbangan = 0
// 	}
// 	cur_frm.set_value("berat", angka);
// 	cur_frm.refresh_field("berat");
// }
// async function appendToTerminal(newStuff, data) {
//   var myVariable = newStuff
//   if (/^ST,/.test(myVariable)) {
// 	console.log("Variabel dimulai dengan 'ST,'");
//   }
//   if (/^S S.*g$/.test(myVariable)) {
// 	console.log("Variabel dimulai dengan 'S S' dan diakhiri dengan 'g'");
//   }
//   if (/.*G S$/.test(myVariable)) {
// 	console.log("Variabel diakhiri dengan 'G S'");
//   }
  
  // newStuff = newStuff.match(/[0-9]*[.]*[0-9]+\w/g);
  // newStuff = newStuff.match(/([0-9]*[.])\w+/s);
  // cur_frm.set_value("berat", flt(newStuff));
  // const valueString = new TextDecoder().decode(value);
  // const filteredValue = newStuff.match(/[-+]?0*(\.\d+)/g).map(x => x.replace(/^[-+]?0*([^0]+)/g, "$1")).join('');
  //   newStuff = newStuff.replace(/ST,\+0*([0-9]+\.[0-9]+)[A-Za-z]*/g, "").trim(); //timbangan suncho dan metler 
  //   let formattedValue = newStuff.replace(".", ",");

//   newStuff = newStuff.replace(/[A-Z]|[a-z]/g, "").trim(); //timbangan suncho dan metler yang bener
//   newStuff = parseFloat(newStuff)

	//and
	// const text = newStuff;
	// const pattern = /ST,\+0*([0-9]+\.[0-9]+)[A-Za-z]*/g;
	// const matches = text.match(pattern);

	// // if (matches) {
	// const angka = matches[0].match(/[0-9]+\.[0-9]+/)[0];
	// console.log(parseFloat(angka)); // Output: 17.66
	// cur_frm.set_value("berat", angka);

	// frappe.model.set_value(data.doctype, data.name, 'qty_penambahan', angka);

	// cur_frm.refresh();

	// }
  // newStuff = newStuff.replace(/[^\d.]/g, "").trim(); //timbangan AND
// }

function hitung(){
	var totalberat = 0,
  	totaltransfer = 0;
	$.each(cur_frm.doc.items, function(i,e){
		// console.log(e.qty_penambahan)
		if(e.qty_penambahan != null){
		totalberat = parseFloat(totalberat) + parseFloat(e.qty_penambahan)
		// console.log(totalberat)
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
				// console.log(total_berat);
			}
			cur_frm.refresh_field('per_kadar');
}
var list_kat = [];
frappe.ui.form.on('Update Bundle Stock', {
	onload:function(frm){
		frm.trigger('get_connect')
	},
	validate: function(frm){
		frm.events.get_disconnect(frm)
	},
	// before_submit: function(frm){
	// 	cur_frm.set_value('status','Submitted')
	// 	frm.refresh();
	// },
	refresh: function(frm) {	
		cur_frm.dashboard.refresh();
		const hasil_timbang = `
			<div class="hasiltimbangan" style="font-weight:bold;margin:0px 13px 0px 2px;
				color:#f9fafa;font-size:18px;display:inline-block;vertical-align:text-bottom;>
				<span class="label_berat">Berat</span>
				<span class="colon">:</span>
				<span class="berat_real">0</span>
			</div>`;
	
		cur_frm.toolbar.page.add_inner_message(hasil_timbang);
		cur_frm.get_field("bundle").set_focus()
		// if( connected == 0){
		frm.add_custom_button(__("Connect"), () => frm.events.get_connect(frm));
		// }else{
		// frm.add_custom_button(__("Disconnect"), () => frm.events.get_disconnect(frm));
		// }
		if (cur_frm.is_new()){
			frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name","id_employee"]).then(function (responseJSON) {
				cur_frm.set_value("pic", responseJSON.message.name);
				cur_frm.set_value("id_employee", responseJSON.message.id_employee);
				cur_frm.get_field("bundle").set_focus()
				cur_frm.refresh_field("pic");
				cur_frm.refresh_field("id_employee");
			//   console.log(responseJSON)
			});
		}		
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
			for(var i = 0; i < records.length; i++){
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
		connected = 0;
		cur_frm.set_value("status_timbangan","Not Connect")
	},
	get_connect: function(frm){
		// frappe.msgprint("Connect");
		window.checkPort = async function (fromWorker) {
			if ("serial" in navigator) {
			  var ports = await navigator.serial.getPorts();
			  if (ports.length == 0 || fromWorker) {
				// console.log("Not Connected");
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
				// console.log("Connected");
				cur_frm.set_value("status_timbangan","Connected")
				cur_frm.refresh_field("status_timbangan");
				// Prompt user to select any serial port.
			  }
			} else {
			  frappe.msgprint("Your browser does not support serial device connection. Please switch to a supported browser to connect to your weigh device");
			}
		  }
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
		hitung();
	},
	timbang: async function(frm,cdt,cdn){
		// sendSerialLine(setQtyPenambahan(frm,cdt,cdn))
		// await sendSerialLine(locals[cdt][cdn])
		frappe.model.set_value(cdt, cdn, 'qty_penambahan', cur_frm.doc.berat);
		cur_frm.refresh_field("items")
	}
});
