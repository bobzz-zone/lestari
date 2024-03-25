// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

var isButtonClicked = false;
var isButtonClicked1 = false;
$(function () {
	$('[data-toggle="tooltip"]').tooltip()
  })
function run_writeoff_sisa(frm){
	if(frm.doc.unallocated_payment>0){
		frm.doc.write_off=frm.doc.write_off+frm.doc.unallocated_payment;
		frm.doc.unallocated_payment=0;
		refresh_field("write_off");
		refresh_field("unallocated_payment");
		frm.doc.total_sisa_invoice=0;
		refresh_field("total_sisa_invoice");
	}
	if(frm.doc.unallocated_idr_payment>0){
		frm.doc.write_off_idr=frm.doc.write_off_idr+frm.doc.unallocated_idr_payment;
		frm.doc.unallocated_idr_payment=0;
		refresh_field("write_off_idr");
		refresh_field("unallocated_idr_payment");
	}
	if (frm.doc.total_sisa_invoice>0){
		if(frm.doc.total_sisa_invoice>0.1){
			frappe.msgprint("Penghapusan Sisa Invoice Melebihi 0.1 Gram Emas di lakukan apabila document ini di submit")
		}
		frm.doc.write_off=frm.doc.write_off-frm.doc.total_sisa_invoice;
		refresh_field("write_off");
		//frm.doc.total_sisa_invoice=0
	}
	$.each(frm.doc.invoice_table,  function(i,  g) {
		frappe.model.set_value(g.doctype, g.name, "allocated", g.outstanding);
	});
	frm.doc.write_off_total=(frm.doc.write_off*frm.doc.tutupan)+frm.doc.write_off_idr;
	refresh_field("write_off_total");
	refresh_total_and_charges(frm);
}
//tax allocated itu di pisah tp kalo un allocated based on mata uang...
function calculate_table_invoice(frm,cdt,cdn){
	var total=0;
	var total_inv=0;
	var total_sisa=0;
	var total_cpr=0;
	var total_pajak=0;
	$.each(frm.doc.invoice_table,  function(i,  g) {
		total=total+g.outstanding;
		total_inv=total_inv+g.total;
		total_sisa=total_sisa+g.outstanding;
		total_pajak=g.outstanding_tax+total_pajak;
	});
	$.each(frm.doc.customer_return,  function(i,  g) {
		total=total+g.outstanding;
		total_cpr=total_cpr+g.outstanding;
	});
	frm.doc.total_pajak=total_pajak;
	frm.doc.total_invoice=total;
	frm.doc.total_24k_inv=total_inv;
	frm.doc.total_sisa_inv=total_sisa;
	frm.doc.total_cpr=total_cpr;
	refresh_field("total_pajak");
	refresh_field("total_invoice");
	refresh_field("total_24k_inv");
	refresh_field("total_sisa_inv");
	refresh_field("total_cpr");
	//frappe.model.set_value(cdt, cdn,"allocated",0);
	frm.doc.discount_amount=Math.floor(frm.doc.bruto_discount/100*frm.doc.discount*1000)/1000;
	refresh_field("discount_amount");
}
function calculate_table_invoice_alo(frm,cdt,cdn){
	var allocated=0;
	var tax_allocated=0;
	$.each(frm.doc.invoice_table,  function(i,  g) {
		allocated=allocated+g.allocated;
		tax_allocated=g.tax_allocated;
	});
	$.each(frm.doc.customer_return,  function(i,  g) {
		allocated=allocated+g.allocated;
	});
	frm.doc.allocated_idr_payment=tax_allocated;
	frm.doc.allocated_payment=allocated ;

	refresh_field("allocated_payment");
	/*refresh_field("unallocated_idr_payment");
	refresh_field("unallocated_payment");*/
	refresh_field("allocated_idr_payment");
	//refresh_field("discount_amount");
	//frappe.msgprint("invoice table reloaded");
}
function refresh_total_and_charges(frm){
	frm.doc.total_extra_charges=Math.floor((frm.doc.total_biaya_tambahan - frm.doc.bonus - frm.doc.discount_amount)*1000)/1000;
	var bonus = frm.doc.bonus ? frm.doc.bonus : 0;
	var diskon = frm.doc.discount_amount ? frm.doc.discount_amount : 0;
	var biaya_tambahan = frm.doc.total_biaya_tambahan ? frm.doc.total_biaya_tambahan : 0;
	var description = "<b style='color:red !important;'>Total Biaya Tambahan = "+ biaya_tambahan +' - Bonus = '+ bonus + " - Discount =" + diskon +"</b>"
	cur_frm.set_df_property('total_extra_charges', 'description', description);
	refresh_field("total_extra_charges");
	console.log(frm.doc.total_extra_charges)
	if (frm.doc.allocated_payment>0){
		if (frm.doc.allocated_payment>frm.doc.total_extra_charges){
			frm.doc.total_sisa_invoice=frm.doc.total_invoice - frm.doc.allocated_payment;
		}else{
			frm.doc.total_sisa_invoice=frm.doc.total_invoice + frm.doc.total_extra_charges - frm.doc.allocated_payment;
		}
	}else{
		frm.doc.total_sisa_invoice=frm.doc.total_invoice + frm.doc.total_extra_charges;
	}
	frm.doc.total_sisa_invoice = frm.doc.total_sisa_invoice+frm.doc.write_off;
	if (frm.doc.total_sisa_invoice <=0 ){
		frm.doc.total_sisa_invoice=0;
	}
	refresh_field("total_sisa_invoice");
}

function calculate_stock_return(frm,cdt,cdn){
	var amount = 0;
	var total = 0;
	$.each(frm.doc.stock_return_transfer,  function(i,  g) {
		amount += g.rate * g.bruto / 100;
		g.amount = g.rate * g.bruto / 100;
		total += amount;
	})
	frm.doc.total_24k_return = total;
	frm.refresh_field("total_24k_return")	
	frm.refresh_field("stock_return_transfer")	
}
function reset_allocated(frm){
	$.each(frm.doc.invoice_table,  function(i,  g) {
		g.allocated=0;
		g.tax_allocated=0;
		frappe.model.set_value(g.doctype, g.name, "allocated", 0);
		frappe.model.set_value(g.doctype, g.name, "tax_allocated", 0);
	});
	$.each(frm.doc.customer_return,  function(i,  g) {
		g.allocated=0;
		frappe.model.set_value(g.doctype, g.name, "allocated", 0);
	});
	frm.doc.allocated_payment=0;
	frm.doc.allocated_idr_payment=0;
	frm.doc.unallocated_idr_payment=frm.doc.total_idr_payment + frm.doc.total_idr_advance;
	frm.doc.unallocated_payment=frm.doc.total_gold_payment + frm.doc.total_gold;
	//frm.doc.unallocated_write_off=0;
	frm.doc.write_off=0;
	frm.doc.write_off_idr=0;
	frm.doc.write_off_total=0;
	frm.doc.jadi_deposit=0;
	refresh_field("allocated_idr_payment");
	refresh_field("allocated_payment");
	refresh_field("unallocated_idr_payment");
	refresh_field("unallocated_payment");
	//refresh_field("unallocated_write_off");
	refresh_field("write_off");
	refresh_field("write_off_idr");
	refresh_field("write_off_total");
	refresh_field("jadi_deposit");
	//frappe.msgprint("Reset Called");
	calculate_table_invoice(frm);
	refresh_total_and_charges(frm);
	calculate_table_advance(frm);
	// frappe.msgprint("Karena ad aperubahan nilai, maka data alokasi dan write off telah ter reset!!");
	frm.dirty()
}
function calculate_table_idr(frm,cdt,cdn){
	var total=0;
	$.each(frm.doc.idr_payment,  function(i,  g) {
		total=total+g.amount;
	});
	frm.doc.total_idr_payment=total;
	frm.doc.total_idr_gold=Math.floor(total*1000/frm.doc.tutupan)/1000;
	refresh_field("total_idr_payment");
	refresh_field("total_idr_gold");
	//calculate total payment
	frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_in_gold;
	frm.doc.unallocated_idr_payment=frm.doc.total_idr_payment + frm.doc.total_idr_advance;
	frm.doc.unallocated_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold-frm.doc.allocated_payment;
	//frappe.msgprint("Callculate IDR");
	refresh_field("total_payment");
	refresh_field("unallocated_payment");
	refresh_field("unallocated_idr_payment");
	var total_idr_payment = frm.doc.total_idr_payment ? frm.doc.total_idr_payment : 0;
	total_idr_payment = total_idr_payment.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
	var tutupan = frm.doc.tutupan ? frm.doc.tutupan : 0;
	tutupan = tutupan.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
	var description = "<b style='color:red !important;'>Total IDR Payment = "+ total_idr_payment +' / Tutupan = '+ tutupan +"</b>"
	cur_frm.set_df_property('total_idr_gold', 'description', description);
	if(frm.doc.allocated_payment!=0){
		reset_allocated(frm);
	}else if(frm.doc.allocated_idr_payment!=0){
		reset_allocated(frm);
	}
}

function calculate_table_stock(frm,cdt,cdn){
	var d=locals[cdt][cdn];
	// frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty/100);
	var total=0;
	$.each(frm.doc.stock_payment,  function(i,  g) {
		total=total+g.amount;
	});
	frm.doc.total_gold_payment=total;
	refresh_field("total_gold_payment");
	//calculate total payment
	frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold;
	refresh_field("total_payment");
	reset_allocated(frm);
	/*frm.doc.unallocated_idr_payment=frm.doc.total_idr_payment+frm.doc.total_idr_advance;
	frm.doc.unallocated_payment=frm.doc.total_gold_payment+frm.doc.total_gold;
	//frappe.msgprint("Callculate Stock");
	refresh_field("unallocated_payment");
	refresh_field("unallocated_idr_payment");*/
}

function formatAngka(angka) {
	let digitDesimal = 4;
	let angkaString = angka.toString();
	let pecahan = angkaString.split('.');
	if (pecahan.length === 2) {
	  // Ambil semua digit sebelum titik dan sejumlah digitDesimal digit setelah titik
	  angkaString = pecahan[0] + '.' + pecahan[1].slice(0, digitDesimal);
	} else {
	  // Jika tidak ada titik desimal, tambahkan .0000 di belakang angka
	  angkaString += '.' + '0'.repeat(digitDesimal);
	}
	angkaString = parseFloat(angkaString)
	angkaString = angkaString.toLocaleString('en-US', { maximumFractionDigits: 4 });
	return angkaString;
  }
function formatBruto(bruto){
	return
}
  
frappe.ui.form.on("Gold Invoice Advance IDR", {
	idr_allocated: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.idr_allocated > d.idr_deposit) {
			frappe.model.set_value(cdt, cdn, "idr_allocated", 0);
			frappe.throw("Allocated cant be higher than deposit value");
		}
		var idr = 0;
		$.each(frm.doc.invoice_advance, function (i, g) {
			if (g.idr_allocated) {
				idr = idr + g.idr_allocated;
			}
		});
		frm.doc.total_idr_in_gold = idr / frm.doc.tutupan;
		frm.doc.total_idr_advance=idr;
		frm.doc.total_advance = frm.doc.total_gold + frm.doc.total_idr_in_gold;
		/*frm.doc.unallocated_idr_payment=frm.doc.total_idr_payment+frm.doc.total_idr_advance;
		frm.doc.unallocated_payment=frm.doc.total_gold_payment+frm.doc.total_gold-frm.doc.allocated_payment;
		refresh_field("unallocated_payment");
		refresh_field("unallocated_idr_payment");*/
		refresh_field("total_idr_in_gold");
		refresh_field("total_advance");
		//if(frm.doc.allocated_payment>0 || frm.doc.allocated_idr_payment>0){
			reset_allocated(frm);
		//}
	},
});
frappe.ui.form.on("Gold Invoice Advance Gold", {
	gold_allocated: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.gold_allocated > d.gold_deposit) {
			frappe.model.set_value(cdt, cdn, "gold_allocated", 0);
			frappe.throw("Allocated cant be higher than deposit value");
		}
		var gold = 0;
		$.each(frm.doc.gold_invoice_advance, function (i, g) {
			if (g.gold_allocated) {
				gold =gold+ g.gold_allocated;
			}
		});
		frm.doc.total_gold = gold;
		frm.doc.total_advance = frm.doc.total_gold + frm.doc.total_idr_in_gold;
		refresh_field("total_advance");
		refresh_field("total_gold");
		/*frm.doc.unallocated_idr_payment=frm.doc.total_idr_payment+frm.doc.total_idr_advance;
		frm.doc.unallocated_payment=frm.doc.total_gold_payment+frm.doc.total_gold-frm.doc.allocated_payment;
		//frappe.msgprint("Gold Allocated");
		refresh_field("unallocated_payment");
		refresh_field("unallocated_idr_payment");*/
		//if(frm.doc.allocated_payment>0 || frm.doc.allocated_idr_payment>0){
			reset_allocated(frm);
		//}
	},
});
frappe.ui.form.on('Gold Payment', {
	onload: function(frm) {
    //     // Get the input field element
    //     var inputField = cur_frm.get_field('tutupan').$input;

    //     // Attach keydown event listener
    //     inputField.keydown(function(event) {
    //         // Check if the Enter key is pressed
    //         if (event.which === 13) {
    //             // Prevent the default Enter key action
    //             event.preventDefault();
    //             return false;
    //         }
    //     });
	var description = 'Total Biaya Tambahan - Bonus + Writeoff - Discount'
	cur_frm.set_df_property("description",description)
    },
    customer:function(frm){
    	frappe.call({
				method: "lestari.gold_selling.doctype.gold_payment.gold_payment.get_latest_transaction",
				args:{customer:frm.doc.customer},
				callback: function (r){
					frm.doc.history_payment=r.message.history;
					refresh_field("history_payment");

				}
			});
    },
	validate:function(frm){
		//validate allocated amount
		if (frm.doc.list_janji_bayar && frm.doc.list_janji_bayar.length>0){
			cur_frm.doc.janji_bayar=frm.doc.list_janji_bayar[0].janji_bayar;
			refresh_field("janji_bayar");
		}
		$.each(frm.doc.invoice_table,  function(i,  g) {
			if (g.allocated>g.outstanding){
				frappe.msgprint("Nota "+g.gold_invoice+" nilai alokasi salah");
				return false;
			}
		});
		$.each(frm.doc.customer_return,  function(i,  g) {
			if (g.allocated>g.outstanding){
				frappe.msgprint("Customer Return "+g.invoice+" nilai alokasi salah");
				return false;
			}
		});
		// frappe.msgprint("JS:"+frm.doc.jadi_deposit)
		var total24kinv = cur_frm.doc.total_24k_inv;
		var totalsisainv = cur_frm.doc.total_sisa_inv;
		var totalgolddepo = cur_frm.doc.total_gold;
		var totalidrdepo = cur_frm.doc.total_idr_advance;
		totalidrdepo = totalidrdepo.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
		var totalgoldpayment = cur_frm.doc.total_gold_payment;
		var bruto_discount = cur_frm.doc.bruto_discount;
		var discount = cur_frm.doc.discount;
		var discount_amount = cur_frm.doc.discount_amount;
		var totalidrpayment = cur_frm.doc.total_idr_payment;
		totalidrpayment = totalidrpayment.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
		var tutupan = cur_frm.doc.tutupan;
		tutupan = tutupan.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
		var write_off_idr = cur_frm.doc.write_off_idr;
		write_off_idr = write_off_idr.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
		var write_off = cur_frm.doc.write_off;
		var write_off_total = cur_frm.doc.write_off_total;
		var total_biaya_tambahan = cur_frm.doc.total_biaya_tambahan;
		var total_pajak = cur_frm.doc.total_pajak;
		total_pajak = total_pajak.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
		var allocated_payment = cur_frm.doc.allocated_payment;
		var allocated_idr_payment = cur_frm.doc.allocated_idr_payment;
		allocated_idr_payment = allocated_idr_payment.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
		var total_advance = cur_frm.doc.total_advance;
		var unallocated_payment = cur_frm.doc.unallocated_payment;
		var unallocated_idr_payment = cur_frm.doc.unallocated_idr_payment;
		unallocated_idr_payment = unallocated_idr_payment.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
		var jadi_deposit = cur_frm.doc.jadi_deposit;
		var total_sisa_invoice = cur_frm.doc.total_sisa_invoice;
		var total_cpr = cur_frm.doc.total_cpr;
		var detail_allocated = "// Detail Allocated Pembayaran";
		
		detail_allocated += "<br> Total 24K Invoice = "+formatAngka(total24kinv);
		
		detail_allocated += "<br> Total Sisa Invoice = "+formatAngka(totalsisainv);
		
		detail_allocated += "<br> Total CPR = "+formatAngka(total_cpr);
		
		detail_allocated += "<br> Total Gold Advance = "+formatAngka(totalgolddepo);
		
		detail_allocated += "<br> Total IDR Advance = "+totalidrdepo;
		
		detail_allocated += "<br> Total Gold Payment = "+formatAngka(totalgoldpayment);
		// detail_allocated += "<br> Bruto Discount = "+formatAngka(bruto_discount);
		// detail_allocated += "<br> Discount = "+discount+" %";
		
		detail_allocated += "<br> Discount Amount = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Bruto Discount'>"+formatAngka(bruto_discount)+"</button> + <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Discount'>"+ discount +" %</button> = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Discount Amount'>" + formatAngka(discount_amount) + "</button>";
		
		detail_allocated += "<br> Total IDR Payment = "+totalidrpayment;
		
		detail_allocated += "<br> Tutupan = "+tutupan;
		
		detail_allocated += "<br> Total Biaya Tambahan = "+formatAngka(total_biaya_tambahan);
		
		detail_allocated += "<br> Total Advance = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total Gold Advance'>"+formatAngka(totalgolddepo)+"</button> + ( <button type='button' class='btn btn-secondary' data-toggle='tooltip' data-placement='top' title='Total IDR Advance'>"+ totalidrdepo +"</button> / <button type='button' class='btn btn-secondary' data-toggle='tooltip' data-placement='top' title='Tutupan'> "+ tutupan +"</button> )";
		
		detail_allocated += "<br> Unallocated = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total Gold Payment'>"+formatAngka(totalgoldpayment)+"</button> + <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total Advance'> "+formatAngka(totalgolddepo)+"</button> = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Unallocated'>"+formatAngka((frm.doc.total_gold_payment+frm.doc.total_gold))+"</button>";
		
		detail_allocated += "<br> Unallocated IDR = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR Payment'>"+totalidrpayment+"</button> + <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR Advance'> "+totalidrdepo+"</button> = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Unallocated IDR'>"+(cur_frm.doc.total_idr_payment+frm.doc.total_idr_advance).toLocaleString('id-ID', { style: 'currency', currency: 'IDR' })+"</button>";
		if( cur_frm.doc.total_idr_payment > 0 || cur_frm.doc.total_idr_advance > 0){
		/// Allocated IDR ///
		detail_allocated += "<br> Allocated IDR = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR Payment'>"+(cur_frm.doc.total_idr_payment+cur_frm.doc.total_idr_advance)+"</button> - <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total Pajak'> "+total_pajak+"</button> = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR Payment - Total Pajak'>"+((cur_frm.doc.total_idr_payment+cur_frm.doc.total_idr_advance)-frm.doc.total_pajak).toLocaleString('id-ID', { style: 'currency', currency: 'IDR' })+"</button>";
		
		detail_allocated += "<br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR Payment'>"+(frm.doc.total_idr_payment-frm.doc.total_pajak).toLocaleString('id-ID', { style: 'currency', currency: 'IDR' })+"</button> / <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Tutupan'> "+tutupan+"</button> = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR Payment / Tutupan'>"+formatAngka((frm.doc.total_idr_payment-frm.doc.total_pajak) / frm.doc.tutupan)+"</button>";

		detail_allocated += "<br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; = ( <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total Invoice'>"+formatAngka(totalsisainv)+"</button> - <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Discount Amount'>"+formatAngka(discount_amount)+"</button> ) - <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR In Gold'> "+formatAngka((frm.doc.total_idr_payment-frm.doc.total_pajak) / frm.doc.tutupan)+"</button> = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Unallocated IDR'>"+formatAngka(((frm.doc.total_sisa_inv-frm.doc.discount_amount)-(frm.doc.total_idr_payment-frm.doc.total_pajak) / frm.doc.tutupan)*frm.doc.tutupan)+"</button>";
		}
		if( cur_frm.doc.total_gold_payment > 0 || cur_frm.doc.total_gold > 0 ){
		/// Allocated Gold ///
		detail_allocated += "<br> Allocated Gold = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total Gold Payment'>"+formatAngka(cur_frm.doc.total_gold_payment)+"</button> + <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total Gold Advance'> "+formatAngka(cur_frm.doc.total_gold)+"</button> = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total Gold Payment + Total Gold Advance'>"+formatAngka((cur_frm.doc.total_gold_payment+cur_frm.doc.total_gold)).toLocaleString('id-ID', { style: 'currency', currency: 'IDR' })+"</button>";
		
		detail_allocated += "<br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR Payment'>"+(cur_frm.doc.total_gold_payment+cur_frm.doc.total_gold)+"</button> - <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Tutupan'> "+tutupan+"</button> = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR Payment / Tutupan'>"+formatAngka((frm.doc.total_idr_payment-frm.doc.total_pajak) / frm.doc.tutupan)+"</button>";

		detail_allocated += "<br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; = ( <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total Invoice'>"+formatAngka(totalsisainv)+"</button> - <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Discount Amount'>"+formatAngka(discount_amount)+"</button> ) - <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Total IDR In Gold'> "+formatAngka((frm.doc.total_idr_payment-frm.doc.total_pajak) / frm.doc.tutupan)+"</button> = <button type='button' class='btn btn-default' data-toggle='tooltip' data-placement='top' title='Unallocated IDR'>"+formatAngka(((frm.doc.total_sisa_inv-frm.doc.discount_amount)-(frm.doc.total_idr_payment-frm.doc.total_pajak) / frm.doc.tutupan)*frm.doc.tutupan)+"</button>";
		}
		cur_frm.doc.detail_allocated =  detail_allocated;
		cur_frm.refresh_fields();
	},
	discount:function(frm){
		if (frm.doc.discount<0){
			return
		}
		frm.doc.discount_amount=Math.floor(frm.doc.bruto_discount/100*frm.doc.discount*1000)/1000;;
		var description = "<b style='color:red !important;'>" + frm.doc.bruto_discount + " * " + frm.doc.discount + " %</b>";
		frm.set_df_property("discount_amount", "description", description)
		refresh_field("discount_amount");
		refresh_total_and_charges(frm);
	},
	bruto_discount:function(frm){
		if (frm.doc.discount<0){
			return
		}
		/*var disc=0
		$.each(frm.doc.invoice_table,  function(i,  g) {
			if (g.allocated>0){
				disc=disc+(g.total_bruto/100*frm.doc.discount);
			}
		});*/
		frm.doc.discount_amount=Math.floor(frm.doc.bruto_discount/100*frm.doc.discount*1000)/1000;
		var discount_amount = frm.doc.discount_amount ? frm.doc.discount_amount : 0;
		var description = "<b style='color:red !important;'>" + frm.doc.bruto_discount + " * " + frm.doc.discount + " %</b>";
		frm.set_df_property("discount_amount", "description", description)
		refresh_field("discount_amount");
		refresh_total_and_charges(frm);
	},
	write_off:function(frm){
		refresh_total_and_charges(frm);
	},
	bonus:function(frm){
		refresh_total_and_charges(frm);
	},
	reset_alokasi:function(frm){
		reset_allocated(frm);
	},
	writeoff_sisa:function(frm){
		//need to change
		run_writeoff_sisa(frm);
	},
	jadikan_deposit:function(frm){
		//need to check
		if (frm.unallocated_idr_payment<=0){
			frm.doc.jadi_deposit=frm.doc.unallocated_payment;
		}else{
			frm.doc.jadi_deposit=frm.doc.unallocated_payment + (frm.doc.unallocated_idr_payment/frm.doc.tutupan); // punya ko bob
		}
		frm.doc.unallocated_payment=0;
		frm.doc.unallocated_idr_payment=0;
		frappe.msgprint("Total Deposit "+frm.doc.jadi_deposit);
		refresh_field("unallocated_payment");
		refresh_field("unallocated_idr_payment");
		refresh_field("jadi_deposit");
		// frm.dirty();
	},
	auto_distribute:function(frm){
		if (frm.doc.invoice_table==[] || frm.doc.customer_return==[]){
			frappe.throw("Tidak ada Invoice yang terpilih");
		}else{
			reset_allocated(frm);
			//payment rupiah selali di alokasikan ke pajak dulu apabila ada pajak
			if (frm.doc.total_pajak>0 && frm.doc.fokus_piutang==0){
				var idr_need_to=frm.doc.unallocated_idr_payment;
				var total_allocated=0;
				$.each(frm.doc.invoice_table,  function(i,  g) {
					if (idr_need_to > g.outstanding_tax){
						g.tax_allocated=g.outstanding_tax;
					}else{
						g.tax_allocated=idr_need_to;
					}
					total_allocated = total_allocated + g.tax_allocated;
					idr_need_to=idr_need_to-g.tax_allocated;
				});
				frm.doc.unallocated_idr_payment=idr_need_to;
				frm.doc.allocated_idr_payment = total_allocated;
				refresh_field("allocated_idr_payment");
			}
			var idr_to_gold=0;
			if (frm.doc.unallocated_idr_payment>0){
				idr_to_gold = (frm.doc.unallocated_idr_payment/frm.doc.tutupan);
				idr_to_gold=parseFloat(idr_to_gold).toFixed(3);
			}
			var saldo_gold=frm.doc.unallocated_payment-frm.doc.total_extra_charges;
			var need_to= parseFloat(saldo_gold) + parseFloat(idr_to_gold);
			if (need_to < 0){
				frappe.throw("Error , Nilai Biaya Tambahan Melebihi Pembayaran yang di lakukan");
			}else if (need_to==0){
				frm.doc.unallocated_payment=0;
				frm.doc.unallocated_idr_payment=0;
			}
			//frappe.msgprint("Need to "+need_to +" dari IDR "+idr_to_gold+" dari GOLD "+saldo_gold);
			// console.log(need_to)
			var sisa_invoice = parseFloat(cur_frm.doc.total_invoice) - parseFloat(need_to) + frm.doc.total_extra_charges ;
			if (sisa_invoice <0){
				sisa_invoice=0;
			}
			cur_frm.set_value("total_sisa_invoice",sisa_invoice);
			refresh_field("total_sisa_invoice");
			need_to = parseFloat(need_to).toFixed(3);
			var total_alo=0;
			// console.log(need_to)
			if(need_to<=0){
				refresh_total_and_charges(frm);
				refresh_field("unallocated_idr_payment");
				//frappe.msgprint("Tidak ada pembayaran yang dapat di alokasikan");
				return;
			}
			$.each(frm.doc.customer_return,  function(i,  g) {
				var alo=0;
				if (need_to>(g.outstanding-g.allocated)){
					alo=g.outstanding-g.allocated;
					//cur_frm.doc.total_sisa_invoice = alo
				}else{
					alo=need_to;
				}
				total_alo=total_alo+alo;
				need_to=need_to-alo;
				frappe.model.set_value(g.doctype, g.name, "allocated", alo);
			});

			if (need_to>0) {
				$.each(frm.doc.invoice_table,  function(i,  g) {
					var alo=0;
					if (need_to>(g.outstanding-g.allocated)){
						alo=g.outstanding-g.allocated;
					}else{
						alo=need_to;
					}
					need_to=need_to-alo;
					total_alo=total_alo+alo;
					frappe.model.set_value(g.doctype, g.name, "allocated", g.allocated+alo);
				});
			}
			/*if (need_to<0){
				frappe.msgprint(" Test "+need_to);
				cur_frm.set_value("total_sisa_invoice",need_to*-1);
				need_to=0;*/
			//}else{
				
			//}	
			//refresh_field("total_sisa_invoice");
			if (idr_to_gold>0){
				var sisa_idr=parseFloat((idr_to_gold-(total_alo-saldo_gold))*frm.doc.tutupan).toFixed(0);
				//jika lebih besar dari yang di hitungdi awal berarti idr nya g kepakai, alias payment enasnya udah cukup
				if (sisa_idr/frm.doc.tutupan>idr_to_gold){
					sisa_idr=idr_to_gold * frm.doc.tutupan;
				}

				frm.doc.unallocated_idr_payment=sisa_idr;
				if (frm.doc.total_pajak>0 && frm.doc.fokus_piutang==1){
					//var idr_need_to=frm.doc.unallocated_idr_payment;
					var total_allocated=0;
					$.each(frm.doc.invoice_table,  function(i,  g) {
						if (sisa_idr > g.outstanding_tax){
							g.tax_allocated=g.outstanding_tax;
						}else{
							g.tax_allocated=idr_need_to;
						}
						total_allocated = total_allocated + g.tax_allocated;
						sisa_idr=sisa_idr-g.tax_allocated;
						
					});
					frm.doc.unallocated_idr_payment=sisa_idr;
					frm.doc.allocated_idr_payment = total_allocated;
					refresh_field("allocated_idr_payment");
				}
				cur_frm.set_value("unallocated_idr_payment",sisa_idr);
			}
			if (saldo_gold <= total_alo){
				frm.doc.unallocated_payment=0;
				cur_frm.set_value("unallocated_payment",0);
			}else{
				//frappe.msgprint(saldo_gold+" - "+total_alo);
				var unaloc=parseFloat(saldo_gold- total_alo).toFixed(3);
				if (unaloc == "" || unaloc == NaN){
					unaloc=0;
				}
				frm.doc.unallocated_payment=unaloc;
				cur_frm.set_value("unallocated_payment",unaloc);
			}

			//frappe.msgprint("Unallocated "+unaloc);
			cur_frm.set_value("allocated_payment",parseFloat(total_alo).toFixed(3));
			refresh_field("unallocated_idr_payment");
			refresh_field("unallocated_payment");
			refresh_field("allocated_payment");
			
			
			var sisa_pay=(frm.doc.unallocated_idr_payment/frm.doc.tutupan) + frm.doc.unallocated_payment;
			if(sisa_pay<=1/100 && sisa_pay>0){
				frappe.msgprint("Write off sisa Sedikit "+(frm.doc.unallocated_idr_payment/frm.doc.tutupan) + frm.doc.unallocated_payment);
				run_writeoff_sisa(frm);
			}if(frm.doc.total_sisa_invoice<=0.01 && frm.doc.total_sisa_invoice>0){
				frappe.msgprint("Write off sisa Invoice Senilai "+frm.doc.total_sisa_invoice);
				run_writeoff_sisa(frm);
			}else{
				refresh_total_and_charges(frm);	
			}
			frappe.msgprint("Pembayaran Telah di Alokasikan");
		}
		frm.dirty()
	},
	tutupan:function(frm){
		cur_frm.get_field("tutupan").set_focus()
		frm.doc.total_idr_gold=frm.doc.total_idr_payment/frm.doc.tutupan;
		var idr = 0;
		$.each(frm.doc.invoice_advance, function (i, g) {
			if (g.idr_allocated) {
				idr = idr + g.idr_allocated;
			}
		});
		frm.doc.total_idr_in_gold = idr / frm.doc.tutupan;
		frm.doc.total_advance = frm.doc.total_gold + frm.doc.total_idr_in_gold;
		refresh_field("total_idr_payment");
		refresh_field("total_advance");
		refresh_field("total_idr_in_gold");
		refresh_field("total_idr_gold");
		//calculate total payment
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold;
		refresh_field("total_payment");
		reset_allocated(frm);
	},
	get_gold_invoice:function(frm){
		// var button = cur_frm.get_field('get_gold_invoice').$input;
		// button.prop('disabled', true);
		// isButtonClicked = true;
		frappe.call({
			method: "get_gold_invoice",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();
				calculate_table_invoice(cur_frm);
				reset_allocated(cur_frm);
				// setTimeout(function() {
				// 	// Check if the button was clicked and disable it
				// 	if (isButtonClicked) {
				// 		button.prop('disabled', true);
				// 	}
				// }, 0);
			}
		});
		
	},
	get_janji_bayar:function(frm){
		// var button = cur_frm.get_field('get_janji_bayar').$input;
		// button.prop('disabled', true);
		// isButtonClicked = true;
		if(cur_frm.doc.list_janji_bayar.length > 0){
			return false;
		}else{
			frappe.call({
				method: "get_janji_bayar",
				doc: frm.doc,
				callback: function (r){
					frm.refresh();	
					// setTimeout(function() {
					// 	// Check if the button was clicked and disable it
					// 	if (isButtonClicked1) {
					// 		button.prop('disabled', true);
					// 	}
					// }, 0);
				}
			});
		}
	},
	refresh: function(frm) {
		// Get the input field element
        // var inputField = cur_frm.get_field('tutupan').$input;

        // // Attach keydown event listener
        // inputField.keydown(function(event) {
        //     // Check if the Enter key is pressed
        //     if (event.which === 13) {
        //         // Prevent the default Enter key action
        //         event.preventDefault();
        //         return false;
        //     }
        // });
		frm.set_query("item","stock_payment", function(doc, cdt, cdn) {
			return {
				"filters": {
					"available_for_stock_payment":1
				}
			};

		});
		frm.set_query("mode_of_payment","idr_payment", function(doc, cdt, cdn) {
			return {
				"filters": [
					["Mode of Payment", "is_sales", "=", "1"],
				]
			};

		});
		frm.set_query("janji_bayar","list_janji_bayar", function(doc, cdt, cdn) {
			return {
				"filters": {
					"customer":doc.customer,
					"jenis_janji":"Pembayaran",
					"status":"Pending"
				}
			};

		});
		frm.set_query("gold_invoice","invoice_table", function(doc, cdt, cdn) {
			return {
				"filters": {
					"docstatus":1,
					"invoice_status":"Unpaid",
					"customer":doc.customer
				}
			};

		});
		frm.set_query("sales_bundle", function(){
			return {
				"filters": [
				["Sales Stock Bundle", "aktif", "=", "1"],
				]
			}
		});

		frm.set_query("customer_deposit", "invoice_advance", function (doc, cdt, cdn) {
			return {
				query: "lestari.gold_selling.doctype.customer_deposit.customer_deposit.get_idr_advance",
				filters: { customer: doc.customer ,subcustomer:doc.subcustomer},
			};
		});
		frm.set_query("customer_deposit", "gold_invoice_advance", function (doc, cdt, cdn) {
			return {
				query: "lestari.gold_selling.doctype.customer_deposit.customer_deposit.get_gold_advance",
				filters: { customer: doc.customer , subcustomer:doc.subcustomer },
			};
		});
		if(!frm.doc.tutupan){
			frappe.call({
				method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
				args:{type:frm.doc.type_emas},
				callback: function (r){
					frm.doc.tutupan=r.message.nilai;
					refresh_field("tutupan");

				}
			});
		}
		if(frm.doc.docstatus > 0) {
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
					company: frm.doc.company,
					group_by: "Group by Voucher (Consolidated)",
					show_cancelled_entries: frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: me.frm.doc.name,
					from_date: me.frm.doc.posting_date,
					to_date: moment(me.frm.doc.modified).format('YYYY-MM-DD'),
					company: me.frm.doc.company,
					show_cancelled_entries: me.frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "Stock Ledger");
			}, __("View"));
		}
	},
	/*type_payment:function(frm){
		frm.doc.idr_payment=[];
		frm.doc.stock_payment=[];
		refresh_field("stock_payment");
		refresh_field("idr_payment")
	},*/
	type_emas:function(frm){
		frm.doc.stock_payment=[];
		refresh_field("stock_payment");
		frappe.call({
                                method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
                                args:{type:frm.doc.type_emas},
                                callback: function (r){
                                        frm.doc.tutupan=r.message.nilai;
                                        refresh_field("tutupan")

                                }
                        });
	}

});

frappe.ui.form.on('Gold Payment Invoice', {
	gold_invoice:function(frm,cdt,cdn) {
		calculate_table_invoice(frm,cdt,cdn);
	},
	allocated:function(frm,cdt,cdn) {
		calculate_table_invoice_alo(frm,cdt,cdn);
		
	},
	invoice_table_remove: function(frm,cdt,cdn){
		calculate_table_invoice(frm,cdt,cdn);
		reset_allocated(frm);
	}
});
frappe.ui.form.on('Gold Payment Return', {
	invoice:function(frm,cdt,cdn) {
		calculate_table_invoice(frm,cdt,cdn);
		frappe.model.set_value(cdt, cdn,"allocated",0);
	},
	allocated:function(frm,cdt,cdn) {
		calculate_table_invoice_alo(frm,cdt,cdn);
		
	}
});
frappe.ui.form.on('IDR Payment', {
	amount:function(frm,cdt,cdn) {
		calculate_table_idr(frm,cdt,cdn)
	},
	idr_payment_remove:function(frm,cdt,cdn){
		calculate_table_idr(frm,cdt,cdn)
	}
});
frappe.ui.form.on('Gold Payment Charges', {
	other_charges_remove:function(frm,cdt,cdn){
		// frappe.msgprint('remove')
		calculate_table_charges(frm,cdt,cdn)
		refresh_total_and_charges(frm)
		reset_allocated(frm);
	},
	category:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		d.amount=0
		d.gold_amount=0
		frappe.model.set_value(cdt, cdn,"gold_amount",0);
		frappe.model.set_value(cdt, cdn,"amount",0);
	},
	gold_amount:function(frm,cdt,cdn) {
		calculate_table_charges(frm,cdt,cdn)
	},
	amount:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		if(d.type=="IDR"){
			frappe.model.set_value(cdt, cdn,"gold_amount",d.amount/frm.doc.tutupan);
		}
		//calculate_table_charges(frm,cdt,cdn)
	}
});
function calculate_table_charges(frm,cdt,cdn){
	var d=locals[cdt][cdn];
	var total=0;
	$.each(frm.doc.other_charges,  function(i,  g) {		
		total=total+g.gold_amount;
	});
	frm.doc.total_biaya_tambahan=total;
	refresh_field("total_biaya_tambahan");
	if(frm.doc.allocated_payment>0){
		reset_allocated(frm);
	}else{
		frm.doc.unallocated_payment=frm.doc.total_gold_payment+frm.doc.total_advance-frm.doc.allocated_payment;
	}
	
}
frappe.ui.form.on('Stock Payment', {
	item:function(frm,cdt,cdn) {
		// your code here
		var d=locals[cdt][cdn];
		if(!d.item){return;}
		frappe.call({
			method: "lestari.gold_selling.doctype.gold_invoice.gold_invoice.get_gold_purchase_rate",
			args:{"item":d.item,"customer":frm.doc.customer,"customer_group":frm.doc.customer_group},
			callback: function (r){
				frappe.model.set_value(cdt, cdn,"rate",r.message.nilai);
				frappe.model.set_value(cdt, cdn,"amount",Math.floor(parseFloat(r.message.nilai)*d.qty*10)/1000);
				var total=0;
				$.each(frm.doc.stock_payment,  function(i,  g) {
					total=total+g.amount;
				});
				frm.doc.total_gold_payment=total;
				refresh_field("total_gold_payment");
				//calculate total payment
				frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold;
				refresh_field("total_payment");
				frm.doc.unallocated_payment=frm.doc.total_gold_payment+frm.doc.total_advance-frm.doc.allocated_payment;
				refresh_field("unallocated_payment");
			}
		});
	},
	qty:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"amount",Math.floor(d.rate*d.qty*10)/1000);
		calculate_table_stock(frm,cdt,cdn)
	},
	rate:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"amount",Math.floor(d.rate*d.qty*10)/1000);
		
		calculate_table_stock(frm,cdt,cdn)
	},
	stock_payment_remove:function(frm,cdt,cdn){
		calculate_table_stock(frm,cdt,cdn)
	}
	
});

frappe.ui.form.on('Gold Invoice Advance IDR', {
	invoice_advance_remove: function(frm,cdt,cdn){
		// console.log("IDR Remove")
		calculate_table_advance(frm,cdt,cdn)
	}
});
frappe.ui.form.on('Gold Invoice Advance Gold', {
	gold_invoice_advance_remove: function(frm,cdt,cdn){
		// console.log("Gold Remove")
		calculate_table_advance(frm,cdt,cdn)
	}
});

frappe.ui.form.on('Gold Payment Return', {
	gold_invoice_advance_remove: function(frm,cdt,cdn){
		// console.log("Gold Remove")
		calculate_table_advance(frm,cdt,cdn)
	}
});

frappe.ui.form.on('Gold Payment Stock Return', {
	rate: function(frm,cdt,cdn){
		calculate_stock_return(frm,cdt,cdn)
	},
	bruto: function(frm,cdt,cdn){
		calculate_stock_return(frm,cdt,cdn)
	},
	stock_return_transfer_remove: function(frm,cdt,cdn){
		calculate_stock_return(frm,cdt,cdn)
	}
});

function calculate_table_advance(frm,cdt,cdn){
	var total_gold=0;
	var total_idr=0;
	var allocated=0;
	$.each(frm.doc.invoice_advance,  function(i,  g) {
		total_idr=total_idr+g.idr_allocated;
		allocated=allocated+parseFloat(g.idr_allocated/frm.doc.tutupan);
	});
	$.each(frm.doc.gold_invoice_advance,  function(i,  g) {
		total_gold=total_gold+g.gold_allocated;
		allocated=allocated+g.gold_allocated;
	});
	// frm.doc.total_invoice=total;
	//frappe.model.set_value(cdt, cdn,"allocated",0);
	// refresh_field("total_invoice");
	frm.doc.total_gold=total_gold ;
	frm.doc.total_idr_advance = total_idr;
	frm.doc.total_idr_in_gold= parseFloat(total_idr) / parseFloat(frm.doc.tutupan) ;
	frm.doc.total_advance=allocated ;
	refresh_field("total_gold");
	refresh_field("total_idr_in_gold");
	refresh_field("total_advance");
	refresh_field("total_idr_advance");
	// frm.doc.unallocated_payment=frm.doc.total_payment + frm.doc.total_advance -frm.doc.allocated_payment;
	// refresh_field("unallocated_payment");
}
