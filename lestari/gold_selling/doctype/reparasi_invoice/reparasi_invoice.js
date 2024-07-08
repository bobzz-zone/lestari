// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

function calculate_items(frm){
	let total_bruto = 0;
	let total_qty = 0;
	$.each(cur_frm.doc.items,  function(i,  g) {	
		total_bruto += g.bruto;
		total_qty += g.qty;
	})
	frm.set_value("total_bruto", total_bruto);
	frm.set_value("total_qty", total_qty);
	frm.refresh_field("total_bruto");
	frm.refresh_field("total_qty");	
}
function calculate_payment_emas(frm){
	let total_24k = 0;
	$.each(cur_frm.doc.payment_emas,  function(i,  g) {	
		total_24k += g.bruto;
	})
	frm.set_value("total_24k", total_24k);
	frm.refresh_field("total_24k");
}

function calculate_jasa(frm){
	let total_idr = 0;
	$.each(cur_frm.doc.harga_reparasi,  function(i,  g) {	
		total_idr += g.amount;
	})
	frm.set_value("total_idr_reparasi", total_idr);
	frm.refresh_field("total_idr_reparasi");
}

frappe.ui.form.on('Reparasi Invoice', {
	
	refresh: function(frm) {
		if (!cur_frm.doc.tutupan) {
			frappe.call({
				method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
				args: { type: cur_frm.doc.type_emas || "CT"},
				callback: function (r) {
					cur_frm.doc.tutupan = r.message.nilai;
					cur_frm.refresh_field("tutupan");
				},
			});
		}
		frm.set_query("jenis_jasa","harga_reparasi", function(doc, cdt, cdn) {
			return {
				"filters": [
					["Item", "item_group", "=", "Services"],
				]
			};

		});
	},
	reparasi_order: function(frm){
		frappe.msgprint(this)
		frappe.call({
			method: "get_order",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();
				calculate_items(frm)
			}
		});
	}
});

frappe.ui.form.on('Reparasi Invoice Items', {
	qty: function(frm, cdt, cdn) {
		calculate_items(frm);
	},
	bruto: function(frm, cdt, cdn) {
		calculate_items(frm);
	},
	items_add: function(frm, cdt, cdn) {
		calculate_items(frm);
	},
	items_remove: function(frm, cdt, cdn) {
		calculate_items(frm);
	},
});

frappe.ui.form.on('Reparasi Invoice Payment IDR', {
	jenis_jasa: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		frappe.db.get_value("Item Price", {"item_code":d.jenis_jasa,"price_list":"Standard Selling"}, "price_list_rate", (value) => {
			d.rate = value.price_list_rate;
			refresh_field("harga_reparasi");
		});
	},
	bruto: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		var amount = 0;
		amount = d.bruto * d.rate;
		d.amount = amount;
		refresh_field("harga_reparasi");
		calculate_jasa(frm);
	},
	rate: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		var amount = 0;
		amount = d.bruto * d.rate;
		d.amount = amount;
		refresh_field("harga_reparasi");
		calculate_jasa(frm);
	}
});

frappe.ui.form.on('Reparasi Invoice Payment Emas', {
	qty: function(frm, cdt, cdn) {
		calculate_payment_emas(frm)
	},
	bruto: function(frm, cdt, cdn) {
		calculate_payment_emas(frm)
	},
	payment_emas_remove: function(frm, cdt, cdn) {
		calculate_payment_emas(frm)
	},
});