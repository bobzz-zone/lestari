// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Janji Bayar', {
	refresh: function(frm) {
		frm.set_query("gold_invoice", function(){
			return {
				"filters": [
					["Gold Invoice", "customer", "=", cur_frm.doc.customer],
					["Gold Invoice", "outstanding", ">", 0.000]
				]
			}
		});
	}
});
