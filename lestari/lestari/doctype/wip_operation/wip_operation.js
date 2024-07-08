// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('WIP Operation', {
	refresh: function(frm) {
		frm.add_custom_button(__("Reset"), () => frm.events.reset_form(frm));
		$(":button[data-label='Reset']").css("background-color", "red");
    	$(":button[data-label='Reset']").css("color", "white");
	},
	reset_form: function(frm){
		frappe.call({
			method: 'reset_wip',
			doc: frm.doc,
			callback: function(r) {
				if(r.message) {
					// frm.set_value('generated_code', r.message);
					cur_frm.refresh();
					cur_frm.refresh_fields();
				}
			}
		});
	}
});
