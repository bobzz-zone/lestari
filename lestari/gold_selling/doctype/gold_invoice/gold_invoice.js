// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gold Invoice', {
	refresh:function(frm) {
		frm.set_query("item_group","items", function(doc, cdt, cdn) {
    			return {
    				"filters": {
    					"is_selling":1
    				}
    			};
    		});
		// your code here
		if(!frm.doc.tutupan){
		    frappe.call({
                method: "lestari.lestari.doctype.gold_rates.gold_rates.get_latest_rates",
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
		var total=0;
		$.each(frm.doc.invoice_advance,  function(i,  g) {
			var gold=0;
			if (g.gold_allocated){
				gold=g.gold_allocated;
			}
			var idr=0;
			if (g.idr_allocated){
				idr=g.idr_allocated/frm.doc.tutupan;
			}
			total=total+gold+idr;
		});
		frm.doc.total_advance=total;
		frm.doc.outstanding=frm.doc.grand_total-frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total_advance");
	}
});

frappe.ui.form.on('Gold Invoice Advance', {
	idr_allocated:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		if (d.idr_allocated>d.idr_deposit){
			frappe.model.set_value(cdt, cdn,"idr_allocated",0);
			frappe.throw("Allocated cant be higher than deposit value");
		}
		var total=0;
		$.each(frm.doc.invoice_advance,  function(i,  g) {
			var gold=0;
			if (g.gold_allocated){
				gold=g.gold_allocated;
			}
			var idr=0;
			if (g.idr_allocated){
				idr=g.idr_allocated/frm.doc.tutupan;
			}
			total=total+gold+idr;
		});
		frm.doc.total_advance=total;
		frm.doc.outstanding=frm.doc.grand_total-frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total_advance");
	},
	gold_allocated:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		if (d.gold_allocated>d.gold_deposit){
			frappe.model.set_value(cdt, cdn,"gold_allocated",0);
			frappe.throw("Allocated cant be higher than deposit value");
		}
		var total=0;
		$.each(frm.doc.invoice_advance,  function(i,  g) {
			var gold=0;
			if (g.gold_allocated){
				gold=g.gold_allocated;
			}
			var idr=0;
			if (g.idr_allocated){
				idr=g.idr_allocated/frm.doc.tutupan;
			}
			total=total+gold+idr;
		});
		frm.doc.total_advance=total;
		frm.doc.outstanding=frm.doc.grand_total-frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total_advance");
	}
});
frappe.ui.form.on('Gold Invoice Item', {
	item_group:function(frm,cdt,cdn) {
		// your code here
		var d=locals[cdt][cdn];
		if(!d.item_group){return;}
		frappe.call({
                method: "lestari.lestari.doctype.gold_invoice.gold_invoice.get_gold_rate",
                args:{"item_group":d.item_group,"customer":frm.doc.customer,"customer_group":frm.doc.customer_group},
                callback: function (r){
                    frappe.model.set_value(cdt, cdn,"rate",r.message.nilai);
                    frappe.model.set_value(cdt, cdn,"amount",parseFloat(r.message.nilai)*d.qty);
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
				    refresh_field("total_advance");
				    refresh_field("total");
				    refresh_field("discount");
				    refresh_field("grand_total");
                	}
                });
		
	},
	qty:function(frm,cdt,cdn) {
	    var d=locals[cdt][cdn];
	    frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty);
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
	    refresh_field("total_advance");
	    refresh_field("total");
	    refresh_field("discount");
	    refresh_field("grand_total");
	}
});
