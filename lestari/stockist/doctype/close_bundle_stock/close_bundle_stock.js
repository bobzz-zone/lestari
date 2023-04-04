// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Close Bundle Stock', {
	refresh: function(frm) {
		frm.set_query("bundle", function(){
			return {
				"filters": [
					["Sales Stock Bundle", "aktif", "=", "1"],
				]
			}
		});
		frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name","id_employee"]).then(function (responseJSON) {
			cur_frm.set_value("pic", responseJSON.message.name);
			// cur_frm.set_value("id_employee", responseJSON.message.id_employee);
			cur_frm.get_field("bundle").set_focus()
			cur_frm.refresh_field("pic");
			// cur_frm.refresh_field("id_employee");
		  //   console.log(responseJSON)
		  })
	},
	bundle: function(frm){
		frappe.call({
			method: 'lestari.stockist.doctype.close_bundle_stock.close_bundle_stock.get_detail_bundle',
			args: {
				bundle: cur_frm.doc.bundle
			},
			callback: (r) => {
				// on success
				console.log(r.message)
				r.message.forEach(element => {
					cur_frm.add_child('items',{
						sub_kategori: element.sub_kategori,
						kategori: element.kategori,
						total_dibawa_sales: element.total_dibawa_sales,
						kadar: element.kadar,
						gold_selling_item: element.gold_selling_item 	
					})
					cur_frm.refresh_field('items');
				});
			},
			error: (r) => {
				// on error
			}
		})
	}
});
frappe.ui.form.on('Detail Close Stock', {
	qty_penambahan: function(frm,cdt,cdn){
		
	}
})