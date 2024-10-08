{% include 'lestari/public/js/custom/custom_multi_select.js' %}

frappe.ui.form.on('Purchase Order', {
	refresh(frm) {
	    // set_row_numbers(frm);
        if(frm.doc.docstatus == 1){
            
            frm.add_custom_button(
               __("Tutup"), function (frm){
                frappe.call({
                    method: "erpnext.buying.doctype.purchase_order.purchase_order.update_status",
                    args: { status: "Closed", name: cur_frm.doc.name },
                    callback: function (r) {
                        cur_frm.set_value("status", "Closed");
                        cur_frm.reload_doc();
                    },
                });
                frappe.call({
                    method: "lestari.custom.custom_purchase_order.tutup_po",
                    args: { status: cur_frm.doc.status, name: cur_frm.doc.name },
                    callback: function (r) {
                        cur_frm.reload_doc();
                    },
                });
               }, 
            )
        }
        frm.add_custom_button(
			__("Purchase Request"),
			async function (frm){
                const allowed_request_types = [
                            "Material Issue",
                ];
                var r = await lestari.utils.map_current_doc({
                    method: "lestari.custom.custom_purchase_order.make_purchase_order",
                    source_doctype: "Purchase Request",
                    target: me.frm,
                    date_field: "transaction_date",
                    setters: [
                        {
                            label: __("Employee"),
                            fieldname: "employee",
                            fieldtype: "Link",
                            options: "Employee",
                            default: cur_frm.doc.employee || undefined,
                        },
                        {
                            fieldtype: "Date",
                            label: __("Transaction Date"),
                            fieldname: "transaction_date",
                        },
                   ],
                   size: "extra-large",
                   get_query_filters: {
                       docstatus: 1,
                   },
                   allow_child_item_selection: true,
                   child_fieldname: "items",
                   child_columns: [
                    "material_request",
                    "idmaterial_request",
                    "ordinal_mr",
                    "transaction_date",
                    "description",
                    "qty",
                    "uom",
                    "proses",
                    "keterangan",
                    ],
                });
                  $(document).on("frappe.ui.Dialog:shown", function() {
                    // Your custom logic here, e.g., perform some action when the dialog is shown
                    if(!r.dialog.fields_dict['allow_child_item_selection'].get_value()){
                        setTimeout(function(){
                            r.dialog.fields_dict.allow_child_item_selection.$input.click();
                        },1000)
                    }
                });
            },
			__("Get Items From")
		);
	},
	before_submit(frm){
        if (frm.doc.data_is_in_erp == 0) {
            set_row_numbers(frm);
            $.each(frm.doc.items,function(i,g){
                if(!g.purchase_request){
                    frappe.throw("Purchase Order harus memiliki Purchase Request!!!")
                }
            })
        }
	},
	on_submit(frm){
	    if(window.name == frm.doc.name){
	        setTimeout(function(){
	            window.close();
	        },2000)
	    }
        setTimeout(function(){cur_frm.reload_doc()}, 3000);
	},
    validate(frm){
        set_row_numbers(frm);
    },
    before_save(frm){
        let asset = 0;
        if(frm.doc.tujuan_doc == "Non Stock"){
            $.each(frm.doc.items,function(i, g){
                if(g.is_fixed_asset){
                    asset = 1;
                    frappe.msgprint("Item "+g.item_code+" Fixed Asset tidak bisa di PO Non Stock, Baris "+g.idx)
                }
            })
            if(asset == 1){
                frappe.throw("Item Fixed Asset tidak bisa di PO Non Stock")
            }
        }
    },
	type_stock(frm){
	     if(frm.doc.type_stock == "STOCK"){
	        frm.set_query("item_code","items", function(frm,cdt,cdn) {
    			return {
    			 "filters":[
		                ["Item","is_stock_item", "=",1],
		                ["Item","is_fixed_asset", "=",0],
		                ["Item","item_group_parent", "=","Pembelian"]
		              ]
    			};

    		});
	    }
	    if(frm.doc.type_stock == "NON STOCK"){
	        frm.set_query("item_code","items", function(frm,cdt,cdn) {
    			return {
    			 "filters":[
		                ["Item","is_stock_item", "=",0],
		                ["Item","is_fixed_asset", "=",0],
		                ["Item","item_group_parent", "=","Pembelian"]
		              ]
    			};

    		});
	    }
	    if(frm.doc.type_stock == "ASSET"){
	        frm.set_query("item_code","items", function(frm,cdt,cdn) {
    			return {
    			 "filters":[
		                ["Item","is_fixed_asset", "=",1],
		              ]
    			};

    		});
	    }
	}
})

frappe.ui.form.on('Purchase Order Item', {
    items_add: function(frm, cdt, cdn) {
        // set_row_numbers(frm);
    },
    items_remove: function(frm, cdt, cdn) {
        // set_row_numbers(frm);
    },
});

function set_row_numbers(frm) {
    // Ambil child table dari form
    let items = frm.doc.items || [];

    // Loop melalui setiap baris dan atur nomor urut
    for (let i = 0; i < items.length; i++) {
        items[i].po_ordinal = i + 1;
    }

    // Refresh grid untuk menampilkan nomor urut yang baru
    frm.refresh_field('items');
}