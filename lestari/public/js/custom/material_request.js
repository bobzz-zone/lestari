frappe.provide("addons.utils");

var list_proses = [];
addons.utils = {
    showColumns: function(frm, fields, table) {
        let grid = frm.get_field(table).grid;
        let re_render = false

        // Menampilkan kolom yang tersembunyi
        for (let field of fields) {
            grid.fields_map[field].in_list_view = 1;
            re_render = true
        }

        // Mengatur ulang kolom yang terlihat
        grid.visible_columns = undefined;
        grid.setup_visible_columns();
        
        // Menghapus header row dan membuat ulang
        grid.header_row.wrapper.remove();
        delete grid.header_row;
        grid.make_head();
        
        
        // Mengembalikan kolom-kolom yang dihapus pada setiap baris
        for (let row of grid.grid_rows) {
            // Menghapus tombol open form
            row.wrapper.children().children('.grid-static-col').remove()
            row.columns = []
            if (row.open_form_button) {
                row.open_form_button.parent().remove();
                delete row.open_form_button;
            }
    
            // Menampilkan Column Baru
            row.render_row();
        }
    },
    removeColumns : function(frm, fields, table) {
        let grid = frm.get_field(table).grid;
        let re_render = false

        for (let field of fields) {
            // console.log(grid.fields_map[field])
            grid.fields_map[field].in_list_view = 0;
            re_render = true
        }
        
        grid.visible_columns = undefined;
        grid.setup_visible_columns();
        
        grid.header_row.wrapper.remove();
        delete grid.header_row;
        grid.make_head();
        
        for (let row of grid.grid_rows) {
            if (row.open_form_button) {
                row.open_form_button.parent().remove();
                delete row.open_form_button;
            }
            
            for (let field in row.columns) {
                if (row.columns[field] !== undefined) {
                    row.columns[field].remove();
                }
            }
            delete row.columns;
            row.columns = [];
            row.render_row();
        }
    }
}

frappe.ui.form.on('Material Request', {
    onload: function(frm){
   
    },
    on_submit: function(frm){
//        setTimeout(function(){cur_frm.reload_doc()}, 3000);
    }, 
    refresh: function(frm) {
        let stock_area = frappe.user.has_role("Stock Area")
        let stock_user = frappe.user.has_role("Stock User")
        if(frappe.user.has_role("Stock Area") && frappe.user.has_role("Stock User") ){
            cur_frm.set_df_property('jenis_mr', 'read_only', 1)
        }

        set_row_numbers(frm);
        if (cur_frm.is_new()){
			frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name","id_employee"]).then(function (responseJSON) {
				cur_frm.set_value("employee_id", responseJSON.message.name);
				cur_frm.set_value("employee_erp", responseJSON.message.name);
				cur_frm.refresh_field("employee_id");
				cur_frm.refresh_field("employee_erp");
			});

            if(frm.doc.material_request_type == "Purchase"){
                frm.doc.naming_series = "MRP.YY..MM..DD..##"
                cur_frm.refresh_field("naming_series")
            }
            if(frm.doc.material_request_type == "Material Issue"){
                frm.doc.naming_series = "MRI.YY..MM..DD..##"
                cur_frm.refresh_field("naming_series")
            }
            if(['Material Transfer','Manufacture','Customer Provided'].includes(frm.doc.material_request_type)){
               frm.doc.naming_series = "MAT-MR-.YYYY.-"
               cur_frm.refresh_field("naming_series")
            }
    
            if(stock_area){
                cur_frm.set_df_property('material_request_type', 'read_only', 1)
                // cur_frm.set_df_property('jenis_dokumen', 'read_only', 1)
            }

            if(frm.doc.jenis_dokumen == "Stock" || frm.doc.jenis_dokumen == ""){
                if(frm.doc.material_request_type == "Purchase" || frm.doc.material_request_type == "Material Issue"){
                    addons.utils.showColumns(frm, ["description"], "items")
                    addons.utils.removeColumns(frm, ["deskripsi_non_stock"], "items")
                    cur_frm.refresh_field("items")
                }
            } 
            if(["Non Stock","Asset"].includes(frm.doc.jenis_dokumen)){
                if(frm.doc.material_request_type == "Purchase" || frm.doc.material_request_type == "Material Issue"){
                    addons.utils.showColumns(frm, ["deskripsi_non_stock"], "items")
                    addons.utils.removeColumns(frm, ["description"], "items")
                    cur_frm.refresh_field("items")
                }
		   }
        //    if(frm.doc.jenis_dokumen == "Bahan Baku"){
        //         frm.set_query('item_code', 'items', function() {
        //             return {
        //                 'filters': {
        //                     'item_group': 'Logam',
        //                     'is_purchase': 0
        //                 }
        //             };
        //         });
        //    }
        }
    },
    before_save: function(frm) {
    if (cur_frm.doc.from_laravel==1){return;}
        set_row_numbers(frm);
        if(cur_frm.doc.jenis_dokumen == "Non Stock")
        $.each(cur_frm.doc.items,function(i,g){
            g.description = g.deskripsi_non_stock
        })
        cur_frm.refresh_field("items")
    },
    material_request_type: function(frm){
        if(frm.doc.jenis_dokumen == "Stock" || frm.doc.jenis_dokumen == ""){
            addons.utils.showColumns(frm, ["description"], "items")
            addons.utils.showColumns(frm, ["idproduct"], "items")
            addons.utils.removeColumns(frm, ["deskripsi_non_stock"], "items")
            cur_frm.refresh_field("items")
        } 
        if(["Non Stock","Asset"].includes(frm.doc.jenis_dokumen)){
            addons.utils.showColumns(frm, ["deskripsi_non_stock"], "items")
            addons.utils.removeColumns(frm, ["description"], "items")
            addons.utils.removeColumns(frm, ["idproduct"], "items")
            cur_frm.refresh_field("items")
        }
        if(frm.doc.material_request_type == "Purchase"){
            frm.doc.naming_series = "MRP.YY..MM..DD..##"
            cur_frm.refresh_field("naming_series")
        }
        if(frm.doc.material_request_type == "Material Issue"){
            frm.doc.naming_series = "MRI.YY..MM..DD..##"
            cur_frm.refresh_field("naming_series")
        }
        if(['Material Transfer','Manufacture','Customer Provided'].includes(frm.doc.material_request_type)){
           frm.doc.naming_series = "MAT-MR-.YYYY.-"
           cur_frm.refresh_field("naming_series")
        }

    },
    jenis_dokumen: function(frm){
        if(frm.doc.jenis_dokumen == "Stock" || frm.doc.jenis_dokumen == ""){
            addons.utils.showColumns(frm, ["description"], "items")
            addons.utils.showColumns(frm, ["idproduct"], "items")
            addons.utils.removeColumns(frm, ["deskripsi_non_stock"], "items")
            cur_frm.refresh_field("items")
            // frappe.msgprint("Stock")
        } 
        if(["Non Stock","Asset"].includes(frm.doc.jenis_dokumen)){
            addons.utils.showColumns(frm, ["deskripsi_non_stock"], "items")
            addons.utils.removeColumns(frm, ["description"], "items")
            addons.utils.removeColumns(frm, ["idproduct"], "items")
            cur_frm.refresh_field("items")
            // frappe.msgprint("Nonstock")
       }
       frm.clear_table("items")
       frm.refresh_fields()
       if (frm.is_new()) {
            frm.add_child('items')
            frm.refresh_field('items');
        }
        if (['izzi@lms.com','niko@lms.com','yonatan@lms.com','gustig@lms.com','aditya@lms.com','Supratno@lms.com','dendro@lms.com'].includes(frappe.session.user)){
            console.log(frappe.session.user)
        }else{
            frm.set_query('proses', 'items', function() {
                return {
                    'filters': {
                        'department': cur_frm.doc.department
                    }
                };
            });
            frappe.db.get_list('Item Group', {
                filters: {
                    'department': cur_frm.doc.department
                }
            }).then(records => {
                for(var i = 0; i < records.length; i++){
                    list_proses.push(records[i].name)
                }
            })
        }
    }
});

frappe.ui.form.on('Material Request Item', {
    items_add: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        set_row_numbers(frm);
        if(['Purchase','Material Issue'].includes(cur_frm.doc.material_request_type) && cur_frm.doc.jenis_dokumen == "Non Stock"){
            console.log('test1')
            console.log(list_proses)
            frappe.model.set_value(cdt, cdn, "proses", list_proses[0]);
            frm.set_df_property('items', 'reqd', 1, frm.docname, 'proses', d.name)
            cur_frm.refresh_field("items");
        }
    },
    items_remove: function(frm, cdt, cdn) {
        set_row_numbers(frm);
    },
    item_code: function(frm, cdt, cdn){
        var d = locals[cdt][cdn];
        if(cur_frm.doc.jenis_dokumen == "Non Stock"){
            d.deskripsi_non_stock = d.description
            cur_frm.refresh_field("items");
        }

        if(['Purchase','Material Issue'].includes(cur_frm.doc.material_request_type) && cur_frm.doc.jenis_dokumen == "Non Stock"){
            console.log('test1')
            frm.set_df_property('items', 'reqd', 1, frm.docname, 'proses', d.name)
            cur_frm.refresh_field("items");
        }
    },
    idproduct: function(frm, cdt, cdn){
        // mendapatkan item_code pada doctype item menggunakan idproduct dan item_group "Pembelian"
        var d = locals[cdt][cdn];
        // console.log("test")
        if(cur_frm.doc.jenis_dokumen == "Stock"){
            frappe.db.get_value("Item", { "idproduct": d.idproduct, "item_group_parent":"Pembelian" }, ["item_code"]).then(function (responseJSON) {
                if(responseJSON.message){
                    frappe.model.set_value(cdt, cdn, "item_code", responseJSON.message.item_code)
                }
            });
        }

        if(['Purchase','Material Issue'].includes(cur_frm.doc.material_request_type) && cur_frm.doc.jenis_dokumen == "Non Stock"){
            console.log('test1')
            frm.set_df_property('items', 'reqd', 1, frm.docname, 'proses', d.name)
            cur_frm.refresh_field("items");
        }
    }
});

function set_row_numbers(frm) {
    // Ambil child table dari form
    let items = frm.doc.items || [];

    // Loop melalui setiap baris dan atur nomor urut
    for (let i = 0; i < items.length; i++) {
        items[i].ordinal = i + 1;
    }

    // Refresh grid untuk menampilkan nomor urut yang baru
    frm.refresh_field('items');
}

cur_frm.cscript.onload = function(doc, cdt, cdn) {
    this.frm.set_query("item_code", "items", function() {
        if (doc.material_request_type == "Customer Provided") {
            return{
                query: "erpnext.controllers.queries.item_query",
                filters:{
                    'customer': me.frm.doc.customer,
                    'is_stock_item':1
                }
            }
        } else if (doc.material_request_type == "Purchase") {
            let prod_con;
            if(cur_frm.doc.material_request_type == "Purchase" && cur_frm.doc.jenis_dokumen === "Stock"){
                prod_con="> 0";
                return{
                    query:"lestari.custom_function.item_query",
        //                query: "erpnext.controllers.queries.item_query",
                        filters: {
                            'item_group_parent': "Pembelian", 
                            "prod_con": prod_con
                        }
                    }
            }else if(cur_frm.doc.material_request_type == "Purchase" && cur_frm.doc.jenis_dokumen === "Batu"){
                return{
                    query:"lestari.custom_function.item_query",
        //                query: "erpnext.controllers.queries.item_query",
                        filters: {
                            'item_group_parent': "Batu"
                        }
                    }
            }else if(cur_frm.doc.material_request_type == "Purchase" && ["Bahan Baku","Campur Bahan"].includes(cur_frm.doc.jenis_dokumen)){
                return{
                    query:"lestari.custom_function.item_query",
        //                query: "erpnext.controllers.queries.item_query",
                        filters: {
                            'item_group': "Logam", 
                            "is_purchase_item": 1
                        }
                    }
            }else if(cur_frm.doc.material_request_type == "Purchase" && ["Asset"].includes(cur_frm.doc.jenis_dokumen)){
                return{
                    query:"lestari.custom_function.item_query",
        //                query: "erpnext.controllers.queries.item_query",
                        filters: {
                            'item_group_parent': "Pembelian", 
                            "is_fixed_asset": 1
                        }
                    }
            }else{
                prod_con="= 0";
                return{
                    query:"lestari.custom_function.item_query",
        //                query: "erpnext.controllers.queries.item_query",
                        filters: {
                            'item_group_parent': "Pembelian", 
                            "prod_con": prod_con
                        }
                    }
            }
            
        } else {
            return{
//                query: "erpnext.controllers.queries.item_query",
		query:"lestari.custom_function.item_query",
                filters: {
                    'item_group_parent': "Pembelian", 
                   // "idproduct":[">","0"],
			        'prod_con':"> 0",
                    'is_stock_item': 1
                }
            }
        }
    });
}
