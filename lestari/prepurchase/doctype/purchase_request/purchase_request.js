// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

function set_row_numbers(frm) {
    // Ambil child table dari form
    let items = frm.doc.items || [];

    // Loop melalui setiap baris dan atur nomor urut
    for (let i = 0; i < items.length; i++) {
        items[i].pr_ordinal = i + 1;
    }

    // Refresh grid untuk menampilkan nomor urut yang baru
    frm.refresh_field('items');
}

function delete_unselected_rows(frm) {
    let grid = frm.fields_dict.items.grid;
    
    let selected_indices = new Set(grid.get_selected_children().map(d => d.idx - 1));
    console.log("Baris terpilih:", selected_indices.size);

    let all_items = frm.doc.items || [];
    console.log("Semua item:", all_items.length);
    
    let unselected_items = all_items.filter((_, index) => !selected_indices.has(index));
    console.log("Item tidak terpilih:", unselected_items.length);
    
    if (!unselected_items.length) {
        frappe.msgprint(__("Tidak ada baris yang tidak terpilih untuk dihapus."));
        return;
    }

    frappe.confirm(__("Anda yakin ingin menghapus {0} baris yang tidak terpilih?", [unselected_items.length]),
        () => {
            frappe.show_progress('Menghapus baris...', 0, 100);
            
            const batchSize = 50;
            const totalBatches = Math.ceil(unselected_items.length / batchSize);
            
            const deleteBatch = (batchIndex) => {
                if (batchIndex >= totalBatches) {
                    frappe.hide_progress();
                    
                    // Mengurutkan ulang indeks item
                    frm.doc.items.forEach((item, index) => {
                        item.idx = index + 1;
                        item.pr_ordinal = index + 1;
                    });
                    
                    frm.refresh_field('items');
                    
                    // Menghilangkan semua centang setelah penghapusan selesai
                    grid.clear_checked_items();
                    
                    frappe.show_alert(__("{0} baris dihapus. Semua centang telah dihapus dan nomor baris telah diurutkan ulang.", [unselected_items.length]));
                    return;
                }

                const start = batchIndex * batchSize;
                const end = Math.min(start + batchSize, unselected_items.length);
                const itemsToDelete = unselected_items.slice(start, end);

                const itemNamesToDelete = new Set(itemsToDelete.map(item => item.name));
                frm.doc.items = frm.doc.items.filter(item => !itemNamesToDelete.has(item.name));

                frappe.show_progress('Menghapus baris...', (batchIndex + 1) * 100 / totalBatches, 100);
                
                setTimeout(() => deleteBatch(batchIndex + 1), 0);
            };

            deleteBatch(0);
        }
    );
}

frappe.ui.form.on('Purchase Request', {
    setup: function(frm){
        
    },
	refresh: function(frm) {
        $(":button[data-fieldname='apply_filter']").css("background-color", "#2490ef");
        $(":button[data-fieldname='apply_filter']").css("color", "white");
        $(":button[data-fieldname='apply_filter']").css("width", "100%");
        $(":button[data-fieldname='reset_filter']").css("background-color", "#fa3c3c");
        $(":button[data-fieldname='reset_filter']").css("color", "white");
        $(":button[data-fieldname='reset_filter']").css("width", "100%");
        if(frm.is_new()){
            if (frm.fields_dict.items && frm.fields_dict.items.grid) {
                // Tambahkan tombol untuk menjalankan fungsi
                frm.add_custom_button(__('Pilih Permintaan'), function() {
                    delete_unselected_rows(frm);
                });
            }
            frm.add_custom_button(__('List MR'), function() {
                frm.call("get_mr_pending").then(() => {
                    frm.refresh_field("items");
                })
            });
            frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name"]).then(function (responseJSON) {
				cur_frm.set_value("employee", responseJSON.message.name);
				cur_frm.refresh_field("employee");
			});
        }
        if(frm.doc.docstatus == 1){
            if(frm.doc.supplier && frm.doc.tujuan_doc){
                frm.add_custom_button(__('Create PO'), function() {
                    console.log('test')
                    frappe.call({
                        doc: frm.doc,
                        method: "create_po",
                        callback: function(response) {
                            if (response.message) {
                                console.log(response.message)
                                // Asumsikan bahwa method create_po mengembalikan nama PO yang baru dibuat
                                var new_po_name = response.message;
                                
                                // Buka form PO yang baru dibuat
                                frappe.set_route("Form", "Purchase Order", new_po_name);
                            }
                        }
                    });
                });
            }
        }
        set_row_numbers(frm);
    },
    on_submit: function(frm) {
        setTimeout(function(){cur_frm.reload_doc()}, 3000);
    },
	tampilkan: function(frm){
		cur_frm.fields_dict.items.grid.grid_pagination.page_length = cur_frm.doc.tampilkan
		cur_frm.refresh_field("items");
		cur_frm.refresh();
	},
	make_custom_buttons: function (frm) {
		frm.add_custom_button(__("Create PO"), () => frm.events.create_po(frm));
    },
    create_po: function(frm){
        frappe.call({
            method: "lestari.prepurchase.doctype.purchase_request.purchase_request.create_po",
            args: {
                doc: frm.doc,
            },
            callback: function(r) {
                if(r.message && !r.exc) {
                    console.log(r.message)
                    frm.set_value("po", r.message);
                }
            }
        })
    },
	reset_filter: function(frm){
        cur_frm.doc.search_by_id_mr = null
        cur_frm.doc.filter_by_proses = null
        cur_frm.doc.sort = null
        cur_frm.doc.sort_by_id_mr = null
        cur_frm.doc.sort_by_proses = null
        cur_frm.refresh_fields();
    },
    apply_filter: function(frm){
        frm.call("get_mr_pending").then(() => {
            frm.refresh_field("items");
        })
    }
});

frappe.ui.form.on('Purchase Request Item', {
	items_add: function(frm, cdt, cdn) {
        set_row_numbers(frm);
    },
    items_remove: function(frm, cdt, cdn) {
        set_row_numbers(frm);
    },
})