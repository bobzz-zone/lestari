// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

function calculate(frm,cdt,cdn){
	var d=locals[cdt][cdn];
		// frappe.model.set_value(cdt, cdn,"amount",Math.floor(d.rate*d.qty*10)/1000);
	frappe.model.set_value(cdt, cdn,"amount",Math.floor(d.qty*(d.rate*10))/1000);
	var total=0;
	frm.doc.total_gold_deposit=0;
	frm.doc.gold_left=0;
	$.each(frm.doc.stock_deposit,  function(i,  g) {
	   	total=total+g.amount;
	});
	frm.doc.total_gold_deposit=total;
	frm.doc.gold_left=total;
	refresh_field("total_gold_deposit");
	refresh_field("gold_left");
}

frappe.ui.form.on('Customer Deposit', {
	on_submit:function(frm){
		cur_frm.reload_doc()
	},
	validate:function(frm){
		if(frm.doc.deposit_type=="Emas"){
			frm.doc.gold_left=frm.doc.total_gold_deposit + frm.doc.total_other_charges_gold;
			refresh_field("gold_left");
		}else{
			frm.doc.idr_left=frm.doc.total_idr_deposit + frm.doc.total_other_charges_idr;
			refresh_field("idr_left");
		}
		console.log(frm.doc.gold_left)
	},
	refresh: function(frm) {
		frm.set_query("sales_bundle", function(){
			return {
				"filters": [
					["Sales Stock Bundle","aktif", "=", "1"],
				]
			}
		});
		frm.set_query("item","stock_deposit", function(doc, cdt, cdn) {
    			return {
    				"filters": [
    					["Item","available_for_stock_payment","=","1"],
    					["Item","item_group","in","Perhiasan, Rongsok, Logam"],
					]
    			};

    		});
		frm.set_query("customer_deposit","source", function (doc) {
	      return {
	        query: "lestari.gold_selling.doctype.customer_deposit.customer_deposit.get_idr_advance",
	        filters: { customer: doc.customer },
	      };
	    });
		if(!frm.doc.tutupan){
		    frappe.call({
                method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
                args:{type:frm.doc.type_emas},
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
	},get_janji_bayar:function(frm){
		frappe.call({
			method: "get_janji_bayar",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();	
			}
		})
		
	},
});
frappe.ui.form.on('Customer Deposit Convert', {
	customer_deposit:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		if (d.covert!=d.nilai){
			frappe.model.set_value(cdt, cdn, "convert", d.convert);
		}
		var total=0;

		$.each(frm.doc.source,  function(i,  g) {
		   	total=total+g.convert;
		});
		frm.doc.total_value_converted=total;
		refresh_field("total_value_converted");
	},
	convert:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		if(d.convert>d.nilai){
			frappe.model.set_value(cdt, cdn, "convert", d.nilai);
			frappe.msgprint("Nilai di gunakan terlalu besar")
		}
		var total=0;

		$.each(frm.doc.source,  function(i,  g) {
		   	total=total+g.convert;
		});
		frm.doc.total_value_converted=total;
		refresh_field("total_value_converted");
	},
	source_remove: function(frm,cdt,cdn){
		var total=0;

		$.each(frm.doc.source,  function(i,  g) {
		   	total=total+g.convert;
		});
		frm.doc.total_value_converted=total;
		refresh_field("total_value_converted");
	}
});
frappe.ui.form.on('IDR Payment', {
	amount:function(frm,cdt,cdn) {
		var total=0;
		$.each(frm.doc.idr_deposit,  function(i,  g) {
		   	total=total+g.amount;
		});
		frm.doc.total_idr_deposit=total;
		frm.doc.idr_left=total;
		refresh_field("total_idr_deposit");
		refresh_field("idr_left");
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
                    frappe.model.set_value(cdt, cdn,"amount",Math.floor(parseFloat(r.message.nilai)*d.qty*10)/1000);
                	var total=0;
				    $.each(frm.doc.stock_deposit,  function(i,  g) {
				    	total=total+g.amount;
				    });
				    frm.doc.total_gold_deposit=total;
				    frm.doc.gold_left=total;
				    refresh_field("total_gold_deposit");
				    refresh_field("gold_left");
				}
                });
				
	},
	stock_deposit_remove:function(frm,cdt,cdn) {
		var total=0;
		$.each(frm.doc.stock_deposit,  function(i,  g) {
		   	total=total+g.amount;
		});
		frm.doc.total_gold_deposit=total;
		frm.doc.gold_left=total;
		refresh_field("total_gold_deposit");
		refresh_field("gold_left");
	},
	qty:function(frm,cdt,cdn) {
	    var d=locals[cdt][cdn];
		calculate(frm,cdt,cdn);
	},
	rate:function(frm,cdt,cdn) {
	    var d=locals[cdt][cdn];
		calculate(frm,cdt,cdn);
	},
	amount_idr:function(frm,cdt,cdn) {
	    var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"qty",Math.floor(d.amount_idr/frm.doc.tutupan)*100/d.rate);
		frappe.model.set_value(cdt, cdn,"amount",Math.floor(d.amount_idr/frm.doc.tutupan));
	}
	
});
frappe.ui.form.on('Gold Payment Charges', {
	other_charges_remove:function(frm,cdt,cdn){
		// frappe.msgprint('remove')
		calculate_other(frm,cdt,cdn);
	},
	category:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		d.amount=0
		d.gold_amount=0
		frappe.model.set_value(cdt, cdn,"gold_amount",0);
		frappe.model.set_value(cdt, cdn,"amount",0);
	},
	gold_amount:function(frm,cdt,cdn) {
		calculate_other(frm,cdt,cdn);
	},
	amount:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		if(d.type=="IDR"){
			frappe.model.set_value(cdt, cdn,"gold_amount",d.amount/frm.doc.tutupan);
		}
		calculate_other(frm,cdt,cdn);
	}
});
function calculate_other(frm,cdt,cdn){
	var d=locals[cdt][cdn];
	var total_gold=0;
	var total_idr=0;
	$.each(frm.doc.other_charges,  function(i,  g) {
	   	total_gold = total_gold + g.gold_amount;
		if(g.gold_amount>0 && g.amount==0){
		   	total_idr = total_idr + (g.gold_amount*frm.doc.tutupan);
		}else{
		   	total_idr = total_idr + g.amount;
		}
	});
	frm.doc.total_other_charges_gold=total_gold;
	frm.doc.total_other_charges_idr=total_idr;
	refresh_field("total_other_charges_gold");
	refresh_field("total_other_charges_idr");
}