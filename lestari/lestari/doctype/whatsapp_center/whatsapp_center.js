// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Whatsapp Center', {
	refresh: function(frm) {
		frm.set_df_property("body_table", "cannot_add_rows", true);
		frm.set_df_property("body_table", "cannot_delete_rows", true);
	},
	template:function(frm){
		cur_frm.clear_table('detail');
		cur_frm.refresh_fields();
		frm.call("get_child",{});
	}
});
