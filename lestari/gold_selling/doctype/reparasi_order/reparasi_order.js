// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

// function calculate_payment_idr(frm){
// 	var total_idr = 0;
// 	$.each(frm.doc.harga_jasa,  function(i,  g) {
// 		total_idr = total_idr + g.amount;
// 	})
// 	frm.set_value("total_idr", total_idr);
// 	frm.refresh_field("total_idr");
// }

function calculate_items(frm){
	var total_bruto = 0;
	var total_qty = 0;
	$.each(frm.doc.items,  function(i, g) {
		total_bruto = total_bruto + g.bruto;
		total_qty = total_qty + g.qty;
	})
	frm.set_value("total_bruto", total_bruto);
	frm.set_value("total_qty", total_qty);
	frm.refresh_field("total_bruto");
	frm.refresh_field("total_qty");	
}

// function calculate_emas_allocated(frm){
// 	var total_allocated = 0;
// 	var total_unallocated = 0;
// 	$.each(frm.doc.detail_payment_emas,  function(i, g) {
// 		if(g.bruto >= g.allocated){
// 			total_allocated = total_allocated + g.allocated;
// 			total_unallocated = total_unallocated + ( g.bruto - g.allocated );
// 		}else{
// 			frappe.throw("Allocated tidak boleh lebih besar dari bruto");
// 		}
// 	})
// 	frm.set_value("total_allocated", total_allocated);
// 	frm.set_value("total_unallocated", total_unallocated);
// 	frm.refresh_field("total_allocated");
// 	frm.refresh_field("total_unallocated");
// }

frappe.ui.form.on('Reparasi Order', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Reparasi Order Items', {
	qty: function(frm, cdt, cdn) {
		calculate_items(frm);
	},
	bruto: function(frm, cdt, cdn) {
		calculate_items(frm);
	},
	items_remove: function(frm, cdt, cdn) {
		calculate_items(frm);
	},
});

// frappe.ui.form.on('IDR Payment', {
// 	amount: function(frm, cdt, cdn) {
// 		calculate_payment_idr(frm);
// 	},
// 	harga_jasa_remove: function(frm, cdt, cdn) {
// 		calculate_payment_idr(frm);
// 	}
// });

// frappe.ui.form.on('Reparasi Order Payment Emas', {
// 	allocated: function(frm, cdt, cdn) {
// 		calculate_emas_allocated(frm);
// 	},
// 	detail_payment_emas_remove: function(frm, cdt, cdn) {
// 		calculate_emas_allocated(frm);
// 	}
// });