frappe.pages['spko-inject'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'SPKO Inject Lilin',
		single_column: true
	});
	page.add_inner_button('Tambah Posts', () => update_posts(),null,'success')
	page.add_inner_button('Edit Posts', () => update_posts(),null,'primary')
	page.add_inner_button('Simpan Posts', () => update_posts(),null,'secondary')
	page.add_inner_button('Hapus Posts', () => update_posts(),null,'danger')
	page.add_inner_button('Update Posts', () => update_posts(),null,'warning')
	wrapper.spko_inject = new SpkoInject(wrapper);

	frappe.breadcrumbs.add("Lestari");
}

SpkoInject = class SpkoInject {
	constructor(wrapper){
		var me = this;
		setTimeout(function() {
			me.setup(wrapper);
			// me.get_data();
		}, 0);
	}

	setup(wrapper) {
		var me = this;
	
		// this.btn_baru = wrapper.page.add_field({"fieldtype": "Button", "fieldname": "btn_baru", "label": __("Baru")})
		// this.btn_ubah = wrapper.page.add_field({"fieldtype": "Button", "fieldname": "btn_ubah", "label": __("Ubah")})
		// this.btn_batal = wrapper.page.add_field({"fieldtype": "Button", "fieldname": "btn_batal", "label": __("Batal")})
		// this.btn_simpan = wrapper.page.add_field({"fieldtype": "Button", "fieldname": "btn_simpan", "label": __("Simpan")})
		this.company_field = wrapper.page.add_field({"fieldtype": "Link", "fieldname": "cari", "options": "SPKO Inject Lilin",
		"label": __("Cari"),
		change: function() {
			me.company = this.value || frappe.defaults.get_user_default('company');
			me.get_data();
			}
		});
	this.section = wrapper.page.add_field({"fieldtype": "Section Break", "fieldname": "sc_1", "label": __("Data lilin")})
	
	}
}