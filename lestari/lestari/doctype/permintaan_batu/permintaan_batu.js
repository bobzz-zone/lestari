// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

var list_kat;
async function getListAndSetQuery(frm) {
list_kat = [];
await frappe.db.get_list('Item Group', {
			filters: {
				parent_item_group: 'Batu'
			}
		}).then(records => {
			for(var i = 0; i< records.length; i++){
				list_kat.push(records[i].name)
			}
			list_kat.sort()
		})
		// console.log(list_kat)
		frm.set_query("item_code", "items",function () {
			return {
				"filters": [
					["Item", "item_group", "in", list_kat],
				],
				"order_by":['name asc']
			};
		});
	}

frappe.ui.form.on('Permintaan Batu', {
	validate: function(frm){
		var total_qty = 0
		$.each(frm.doc.items, function(i,e){
			total_qty += e.qty
		})
		frm.set_value("total_qty",total_qty)
		refresh_field("total_qty")
	},
	refresh: function(frm) {
		getListAndSetQuery(frm);
		if (cur_frm.is_new()){
			frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name","id_employee"]).then(function (responseJSON) {
				cur_frm.set_value("employee", responseJSON.message.name);
				cur_frm.set_value("id_employee", responseJSON.message.id_employee);
				cur_frm.refresh_field("employee");
				cur_frm.refresh_field("id_employee");
			});
		}
	}
});
