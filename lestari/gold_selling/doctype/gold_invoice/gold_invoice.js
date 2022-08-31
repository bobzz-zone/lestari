// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gold Invoice', {
	refresh:function(frm) {
		// your code here
		if(!frm.doc.tutupan){
		    frappe.call({
                method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
                callback: function (r){
                    frm.doc.tutupan=r.message.nilai;
                    refresh_field("tutupan")
                
                	}
                })
		}
	},
	discount:function(frm){
		if (!frm.doc.discount){
	    	frm.doc.discount=0;
	    }
	    frm.doc.grand_total=frm.doc.total-frm.doc.discount;
	    if (!frm.doc.total_advance){
	    	frm.doc.total_advance=0;
	    }
	    frm.doc.outstanding=frm.doc.grand_total-frm.doc.total_advance;
	    refresh_field("outstanding");
	    refresh_field("grand_total");
	},
	tutupan:function(frm){
		var idr=0;
		$.each(frm.doc.invoice_advance,  function(i,  g) {
			if (g.idr_allocated){
				idr=idr+g.idr_allocated;
			}
		});
		frm.doc.total_idr_in_gold=idr/frm.doc.tutupan
		frm.doc.total_advance=frm.doc.total_gold+frm.doc.total_idr_in_gold;
		frm.doc.outstanding=frm.doc.grand_total-frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total_idr_in_gold");
		refresh_field("total_advance");
	}
});
frappe.ui.form.on('Gold Invoice Advance IDR', {
	idr_allocated:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		if (d.idr_allocated>d.idr_deposit){
			frappe.model.set_value(cdt, cdn,"idr_allocated",0);
			frappe.throw("Allocated cant be higher than deposit value");
		}
		var idr=0;
		$.each(frm.doc.invoice_advance,  function(i,  g) {
			if (g.idr_allocated){
				idr=idr+g.idr_allocated;
			}
		});
		frm.doc.total_idr_in_gold=idr/frm.doc.tutupan;
		frm.doc.total_advance=frm.doc.total_gold+frm.doc.total_idr_in_gold;
		frm.doc.outstanding=frm.doc.grand_total-frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total_idr_in_gold");
		refresh_field("total_advance");
	}
});
frappe.ui.form.on('Gold Invoice Advance Gold', {
	
	gold_allocated:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		if (d.gold_allocated>d.gold_deposit){
			frappe.model.set_value(cdt, cdn,"gold_allocated",0);
			frappe.throw("Allocated cant be higher than deposit value");
		}
		var gold=0;
		$.each(frm.doc.gold_invoice_advance,  function(i,  g) {
			if (g.gold_allocated){
				gold=g.gold_allocated;
			}
		});
		frm.doc.total_gold=gold;
		frm.doc.total_advance=frm.doc.total_gold+frm.doc.total_idr_in_gold;
		frm.doc.outstanding=frm.doc.grand_total-frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total_advance");
		refresh_field("total_gold");
	}
});
frappe.ui.form.on('Gold Invoice Item', {
	category:function(frm,cdt,cdn) {
		// your code here
		var d=locals[cdt][cdn];
		if(!d.category){return;}
		frappe.call({
                method: "lestari.gold_selling.doctype.gold_invoice.gold_invoice.get_gold_rate",
                args:{"category":d.category,"customer":frm.doc.customer,"customer_group":frm.doc.customer_group},
                callback: function (r){
                    frappe.model.set_value(cdt, cdn,"rate",r.message.nilai);
                    frappe.model.set_value(cdt, cdn,"amount",parseFloat(r.message.nilai)*d.qty/100);
                	var total=0;
				    $.each(frm.doc.items,  function(i,  g) {
				    	total=total+g.amount;
				    });
				    frm.doc.total=total;
				    if (!frm.doc.discount){
				    	frm.doc.discount=0;
				    }
				    frm.doc.grand_total=frm.doc.total-frm.doc.discount;
				    if (!frm.doc.total_advance){
				    	frm.doc.total_advance=0;
				    }
				    frm.doc.outstanding=frm.doc.grand_total-frm.doc.total_advance;
				    refresh_field("outstanding");
				    refresh_field("total");
				    refresh_field("discount");
				    refresh_field("grand_total");
                	}
                });
		
	},
	qty:function(frm,cdt,cdn) {
	    var d=locals[cdt][cdn];
	    frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty/100);
	    var total=0;
	    $.each(frm.doc.items,  function(i,  g) {
	    	total=total+g.amount;
	    });
	    frm.doc.total=total;
	    if (!frm.doc.discount){
			frm.doc.discount=0;
		}
	    frm.doc.grand_total=frm.doc.total-frm.doc.discount;
	    if (!frm.doc.total_advance){
	    	frm.doc.total_advance=0;
	    }
	    frm.doc.outstanding=frm.doc.grand_total-frm.doc.total_advance;
	    refresh_field("outstanding");
	    refresh_field("total");
	    refresh_field("discount");
	    refresh_field("grand_total");
	}
});
