// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Serah Terima Payment Cash', {
	refresh: function (frm) {
		// frm.fields_dict.details.grid.grid_buttons.addClass("hidden");
		// frm.set_df_property("details", "cannot_add_rows", true);
		// frm.set_df_property("details", "cannot_delete_rows", true);
		if (frm.doc.docstatus > 0) {
			cur_frm.add_custom_button(
			__("Accounting Ledger"),
			function () {
				frappe.route_options = {
				voucher_no: frm.doc.voucher_no,
				from_date: frm.doc.posting_date,
				to_date: moment(frm.doc.modified).format("YYYY-MM-DD"),
				company: frm.doc.company,
				group_by: "",
				show_cancelled_entries: frm.doc.docstatus === 2,
				};
				frappe.set_route("query-report", "General Ledger");
			},
			__("View")
			);
		}
	  },
	  sales: function (frm){
		if(cur_frm.doc.sales){
			frm.set_query('bundle',function(frm){
				return {
					"filters":[
						["Sales Stock Bundle","sales","=",cur_frm.doc.sales]
					]	
				}	
			})
		}else{
			frm.set_query('bundle',function(frm){
				return {
					"filters":[
			
					]	
				}	
			})
		}
	  }
});
frappe.ui.form.on("Serah Terima Payment Cash Deposit", {
	// refresh: function(frm) {
  
	// }
	payment_remove: function (frm, cdt, cdn) {
		console.log(cur_frm.doc.nilai_cash)
		var total_amount = 0
		$.each(frm.doc.payment, function (i, g) {
			total_amount = total_amount + g.amount	
			console.log(total_amount)		
		})
		cur_frm.doc.nilai_cash = total_amount
		cur_frm.refresh_field('nilai_cash')
	//   var d = locals[cdt][cdn];
	  // cur_frm.get_field("items").grid.grid_rows_by_docname[d.name].remove();
	//   cur_frm.get_field("details").grid.grid_rows[d.idx - 1].remove();
	//   cur_frm.refresh_field("details");
	},
  });