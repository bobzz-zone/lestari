// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

function calculate_table_invoice(frm,cdt,cdn){
	var total=0;
		var allocated=0;
		$.each(frm.doc.invoice_table,  function(i,  g) {
		   	total=total+g.outstanding;
		   	allocated=allocated+g.allocated;
		});
		$.each(frm.doc.customer_return,  function(i,  g) {
			total=total+g.outstanding;
			allocated=allocated+g.allocated;
		});
		frm.doc.total_invoice=total;
		frappe.model.set_value(cdt, cdn,"allocated",0);
		refresh_field("allocated");
		refresh_field("total_invoice");
		frm.doc.allocated_payment=allocated;
		refresh_field("allocated_payment");
		frm.doc.unallocated_payment=frm.doc.total_payment+frm.doc.allocated_payment;
		refresh_field("unallocated_payment");
		
}
function reset_allocated(frm){
	$.each(frm.doc.invoice_table,  function(i,  g) {
		g.allocated=0;
		frappe.model.set_value(g.doctype, g.name, "allocated", 0);
	});
	$.each(frm.doc.customer_return,  function(i,  g) {
		g.allocated=0;
		frappe.model.set_value(g.doctype, g.name, "allocated", 0);
	});
	frm.doc.allocated_payment=0;
	refresh_field("allocated_payment");
	frm.doc.unallocated_payment=frm.doc.total_payment + frm.doc.total_advance;
	refresh_field("unallocated_payment");
	frm.doc.unallocated_write_off=0;
	refresh_field("unallocated_write_off");
	frm.doc.jadi_deposit=0;
	refresh_field("jadi_deposit");
	frappe.msgprint("Data Alokasi Ter Reset , silahkan distribusi ulang");
}
function calculate_table_idr(frm,cdt,cdn){
	var total=0;
	$.each(frm.doc.idr_payment,  function(i,  g) {
		   	total=total+g.amount;
		});
		frm.doc.total_idr_payment=total;
		frm.doc.total_idr_gold=total/frm.doc.tutupan;
		refresh_field("total_idr_payment");
		refresh_field("total_idr_gold");
		//calculate total payment
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		frm.doc.unallocated_payment=frm.doc.total_payment-frm.doc.allocated_payment;
		refresh_field("total_payment");
		if(frm.doc.unallocated_payment<0){
			reset_allocated(frm);
		}else{
			refresh_field("unallocated_payment");

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
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("total_payment");
		frm.doc.unallocated_payment=frm.doc.total_payment-frm.doc.allocated_payment;
		refresh_field("unallocated_payment");
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
	  frm.doc.total_advance = frm.doc.total_gold + frm.doc.total_idr_in_gold;
	  refresh_field("total_idr_in_gold");
	  refresh_field("total_advance");
	  if(frm.doc.allocated_payment>0){
	  	reset_allocated(frm);
	  }
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
		  gold = g.gold_allocated;
		}
	  });
	  frm.doc.total_gold = gold;
	  frm.doc.total_advance = frm.doc.total_gold + frm.doc.total_idr_in_gold;
	  refresh_field("total_advance");
	  refresh_field("total_gold");
	  if(frm.doc.allocated_payment>0){
	  	reset_allocated(frm);
	  }
	 },
  });

frappe.ui.form.on('Gold Payment', {
	discount:function(frm){
		if (frm.doc.discount<=0){
			return
		}
		/*var disc=0
		$.each(frm.doc.invoice_table,  function(i,  g) {
			if (g.allocated>0){
				disc=disc+(g.total_bruto/100*frm.doc.discount);
			}
		 });*/
		frm.doc.discount_amount=frm.doc.bruto_discount*frm.doc.discount/100;
		refresh_field("total_payment");
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("discount_amount");
	},
	bruto_discount:function(frm){
		if (frm.doc.discount<=0){
			return
		}
		/*var disc=0
		$.each(frm.doc.invoice_table,  function(i,  g) {
			if (g.allocated>0){
				disc=disc+(g.total_bruto/100*frm.doc.discount);
			}
		 });*/
		frm.doc.discount_amount=frm.doc.bruto_discount*frm.doc.discount/100;
		refresh_field("total_payment");
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("discount_amount");
	},
	write_off:function(frm){
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("total_payment");
	},
	bonus:function(frm){
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("total_payment");
	},
	writeoff_sisa:function(frm){
		frm.doc.write_off=frm.doc.write_off-frm.doc.unallocated_payment;
		frm.doc.unallocated_payment=0;
		if (frm.doc.total_sisa_invoice>0.1){
			if(frm.doc.total_sisa_invoice>0.1){
				frappe.msgprint("Penghapusan Sisa Invoice Melebihi 0.01 Gram Emas di lakukan apabila document ini di submit")
			}
			frm.doc.write_off=frm.doc.write_off+frm.doc.total_sisa_invoice;
			refresh_field("total_sisa_invoice");
		}
		refresh_field("unallocated_payment");
		refresh_field("write_off");
	},
	jadikan_deposit:function(frm){
		frm.doc.jadi_deposit=frm.doc.unallocated_payment+frm.doc.write_off;
		frm.doc.unallocated_payment=0;
		refresh_field("unallocated_payment");
		refresh_field("jadi_deposit");
		frm.dirty();
	},
	auto_distribute:function(frm){
		if (frm.doc.invoice_table==[] && frm.doc.customer_return==[]){
			frappe.throw("Tidak ada Invoice yang terpilih");
		}else{
			var need_to=frm.doc.unallocated_payment;
			// console.log(need_to)
			var sisa_invoice = parseFloat(cur_frm.doc.total_invoice) - parseFloat(need_to)
			cur_frm.set_value("total_sisa_invoice",sisa_invoice)
			cur_frm.refresh_field("total_sisa_invoice")
			need_to = need_to.toFixed(3);
			// console.log(need_to)
			if(need_to<=0){
				frappe.throw("Tidak ada pembayaran yang dapat di alokasikan");
			}
			$.each(frm.doc.customer_return,  function(i,  g) {
				var alo=0;
		   		if (need_to>(g.outstanding-g.allocated)){
		   			alo=g.outstanding-g.allocated;
					cur_frm.doc.total_sisa_invoice = alo
		   		}else{
		   			alo=need_to;
		   		}
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
			   		frappe.model.set_value(g.doctype, g.name, "allocated", g.allocated+alo);
			   	});
			}
			// frm.doc.unallocated_payment=need_to;
			cur_frm.set_value("unallocated_payment",need_to.toFixed(3))
			// console.log(cur_frm.doc.unallocated_payment)
			refresh_field("unallocated_payment");
			frappe.msgprint("Pembayaran Telah di Alokasikan");

		}

	},
	tutupan:function(frm){
		var total=0;
		$.each(frm.doc.idr_payment,  function(i,  g) {
		   	total=total+g.amount;
		});
		frm.doc.total_idr_payment=total;
		frm.doc.total_idr_gold=total/frm.doc.tutupan;
		refresh_field("total_idr_payment");
		refresh_field("total_idr_gold");
		//calculate total payment
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("total_payment");
		frm.doc.unallocated_payment=frm.doc.total_payment-frm.doc.allocated_payment;
		refresh_field("unallocated_payment");
	},
	refresh: function(frm) {
		frm.set_query("item","stock_payment", function(doc, cdt, cdn) {
    			return {
    				"filters": {
    					"available_for_stock_payment":1
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
                callback: function (r){
                    frm.doc.tutupan=r.message.nilai;
                    refresh_field("tutupan")
                
                	}
                })
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
	}

});

frappe.ui.form.on('Gold Payment Invoice', {
	gold_invoice:function(frm,cdt,cdn) {
		calculate_table_invoice(frm,cdt,cdn)
	},
	allocated:function(frm,cdt,cdn) {
		var allocated=0;
		var bruto=0
		$.each(frm.doc.invoice_table,  function(i,  g) {
			if (g.allocated>0){
				bruto=bruto+g.total_bruto;
		   		allocated=allocated+g.allocated;
			}
		});
		$.each(frm.doc.customer_return,  function(i,  g) {
			if (g.allocated>0){
				allocated=allocated+g.allocated;
			}
		});
		//frm.doc.bruto_discount=bruto;
		frm.doc.discount_amount=bruto/100*frm.doc.discount;
		frm.doc.allocated_payment=allocated;
		refresh_field("discount_amount");
		refresh_field("allocated_payment");
		frm.doc.unallocated_payment=frm.doc.total_payment-frm.doc.allocated_payment;
		refresh_field("unallocated_payment");
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("discount_amount");
	},
	invoice_table_remove: function(frm,cdt,cdn){
		calculate_table_invoice(frm,cdt,cdn)
	}
});
frappe.ui.form.on('Gold Payment Return', {
	invoice:function(frm,cdt,cdn) {
		var total=0;
		var allocated=0;
		$.each(frm.doc.invoice_table,  function(i,  g) {
		   	total=total+g.outstanding;
		   	allocated=allocated+g.allocated;
		});
		$.each(frm.doc.customer_return,  function(i,  g) {
			total=total+g.outstanding;
			allocated=allocated+g.allocated;
		});
		frm.doc.total_invoice=total;
		frappe.model.set_value(cdt, cdn,"allocated",0);
		refresh_field("allocated");
		refresh_field("total_invoice");
		frm.doc.allocated_payment=allocated;
		refresh_field("allocated_payment");
		frm.doc.unallocated_payment=frm.doc.total_payment+frm.doc.allocated_payment;
		refresh_field("unallocated_payment");

	},
	allocated:function(frm,cdt,cdn) {
		var allocated=0;
		var bruto=0
		$.each(frm.doc.invoice_table,  function(i,  g) {
			if (g.allocated>0){
				bruto=bruto+g.total_bruto;
		   		allocated=allocated+g.allocated;
			}
		});
		$.each(frm.doc.customer_return,  function(i,  g) {
			if (g.allocated>0){
				allocated=allocated+g.allocated;
			}
		});
		//frm.doc.bruto_discount=bruto;
		frm.doc.discount_amount=bruto/100*frm.doc.discount;
		frm.doc.allocated_payment=allocated;
		refresh_field("discount_amount");
		refresh_field("allocated_payment");
		frm.doc.unallocated_payment=frm.doc.total_payment-frm.doc.allocated_payment;
		refresh_field("unallocated_payment");
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
		refresh_field("discount_amount");
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
				frappe.model.set_value(cdt, cdn,"amount",parseFloat(r.message.nilai)*d.qty/100);
				var total=0;
				$.each(frm.doc.stock_payment,  function(i,  g) {
					total=total+g.amount;
				});
				frm.doc.total_gold_payment=total;
				refresh_field("total_gold_payment");
				//calculate total payment
				frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold+frm.doc.write_off+frm.doc.discount_amount+frm.doc.bonus;
				refresh_field("total_payment");
				frm.doc.unallocated_payment=frm.doc.total_payment-frm.doc.allocated_payment;
				refresh_field("unallocated_payment");
			}
		});
	},
	qty:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty/100);
		calculate_table_stock(frm,cdt,cdn)
	},
	rate:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty/100);
		calculate_table_stock(frm,cdt,cdn)
	},
	stock_payment_remove:function(frm,cdt,cdn){
		calculate_table_stock(frm,cdt,cdn)
	}
	
});

