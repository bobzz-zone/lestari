// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Form Hasil Job Card', {
	refresh: function(frm) {
		  frm.set_query("kadar", function () {
			return {
			  query: "lestari.lestari.doctype.form_hasil_job_card.form_hasil_job_card.get_kadar",
			  filters: {
				parent: frm.doc.no_job_card,
			  },
			};
		  });
	}
});
