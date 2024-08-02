{% include 'lestari/public/js/custom/custom_multi_select.js' %}
// frappe.provide("lestari.utils");

frappe.ui.form.on('Stock Entry', {
    // onload: function(frm) {
    //     const opts = {
    //         frm: frm,
    //         warehouse_field: 'warehouse',
    //         item_field: 'item_code',
    //         child_doctype: 'Your Child Doctype',
    //         original_item_field: 'original_item_field',
    //         condition: (d) => true,
    //         child_docname: 'items'
    //     };

    //     const warehouse_field = opts.warehouse_field || 'warehouse';
    //     const item_field = opts.item_field || 'item_code';

    //     this.data = [];
    //     const dialog = new frappe.ui.Dialog({
    //         title: __("Select Material Request Item"),
    //         fields: [
    //             { fieldtype: 'Section Break', label: __('Items') },
    //             {
    //                 fieldname: "alternative_items",
    //                 fieldtype: "Table",
    //                 cannot_add_rows: true,
    //                 in_place_edit: true,
    //                 data: this.data,
    //                 get_data: () => {
    //                     return this.data;
    //                 },
    //                 fields: [
    //                     // Your table fields here
    //                 ]
    //             },
    //         ],
    //         primary_action: function() {
    //             // Your primary action logic here
    //         },
    //         primary_action_label: __('Update')
    //     });

    //     frm.doc[opts.child_docname].forEach(d => {
    //         if (!opts.condition || opts.condition(d)) {
    //             dialog.fields_dict.alternative_items.df.data.push({
    //                 "docname": d.name,
    //                 "item_code": d[item_field],
    //                 "warehouse": d[warehouse_field],
    //                 "actual_qty": d.actual_qty
    //             });
    //         }
    //     });

    //     this.data = dialog.fields_dict.alternative_items.df.data;
    //     dialog.fields_dict.alternative_items.grid.refresh();
    //     dialog.show();
    // },
    on_submit: function(frm){
        if(frm.doc.stock_entry_type == "Transfer Area"){
            if(frm.doc.id_transfer_erp){
                return
            }else{
                frappe.throw("ID Transfer ERP harus diisi");
            }
        }
    },
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) {
		    frm.events.make_custom_buttons(frm);
        }
    },
    after_save: function(frm){
      setTimeout(function(){cur_frm.reload_doc()}, 3000);
    },

	make_custom_buttons: function (frm) {
		frm.add_custom_button(__("Material Request ERP"), () => frm.events.get_item_mr(frm), __("Get Items From"));
// 		frm.add_custom_button(__("Material Request ERP1"), () => frm.events.test_dialog(frm), __("Get Items From"));
	},
	
	test_dialog: function (frm){
	    // frappe.msgprint("test")


        const dialog = new frappe.ui.Dialog({
            title: __("List Material Request Item"),
            size: "extra-large",
            fields: [
                {
                    fieldname: "material_request",
                    fieldtype: "Link",
                    label: __("Material Request"),
                    options: "Material Request",
                },
                {
                    fieldname: "idmaterial_request",
                    fieldtype: "Data",
                    label: __("ID Material Request"),
                },
                {
                    fieldtype: "Column Break",
                },
                {
                    fieldname: "department",
                    fieldtype: "Link",
                    label: __("Department"),
                    options: "Department",
                    default: me.frm.doc.department || undefined,
                },
                {
                    fieldtype: "Column Break",
                },
                {
                    fieldname: "stock_entry_type",
                    fieldtype: "Link",
                    label: __("Stock Entry Type"),
                    options: "Stock Entry Type",
                    default: "Material Issue",
                },
                {
                    fieldtype: "Section Break",
                },
                {
                    fieldname: "detail",
                    fieldtype: "Table",
                    label: __("Detail"),
                    // in_place_edit: false,
                    // allow_bulk_edit: false,
					// cannot_add_rows: true,
					// cannot_delete_rows: true,
                    read_only: 1,
                    reqd: 1,
                    fields: [
                        {
                            fieldname: "parent",
                            label: __("Material Request"),
                            fieldtype: "Link",
                            options: "Material Request",
                            in_list_view: 1,
                            reqd: 1,
                            columns: 2
                        },
                        {
                            fieldname: "item_code",
                            label: __("Item Code"),
                            fieldtype: "Link",
                            options: "Item",
                            in_list_view: 1,
                            columns: 2,
                        },
                        {
                            fieldname: "description",
                            label: __("Description"),
                            fieldtype: "Text",
                            in_list_view: 1,
                            columns: 2,
                        },
                        {
                            fieldname: "qty",
                            label: __("Qty"),
                            fieldtype: "Float",
                            in_list_view: 1,
                            columns: 1,
                        },
                        {
                            fieldname: "uom",
                            label: __("UOM"),
                            fieldtype: "Link",
                            fieldtype: "UOM",
                            in_list_view: 1,
                            columns: 1,
                        },
                        {
                            fieldname: "ordinal",
                            label: __("Ordinal"),
                            fieldtype: "Int",
                            in_list_view: 1,
                            columns: 1,
                        },
                        {
                            fieldname: "warehouse",
                            label: __("Warehouse"),
                            fieldtype: "Link",
                            options: "Warehouse",
                            in_list_view: 1,
                            columns: 1,
                        }
                    ],
                    on_add_row: (idx) => {
                        // idx = visible idx of the row starting from 1
                        // eg. set `log_type` as alternating IN/OUT in the table on row addition
                        let data_id = idx - 1;
                        let logs = dialog.fields_dict.logs;
                        let log_type = (data_id % 2) === 0 ? "IN" : "OUT";
        
                        logs.df.data[data_id].log_type = log_type;
                        logs.grid.refresh();
                    },
                },
            ],
            primary_action: (values) => {
                // primary action logic here
            },
            primary_action_label: __("Create"),
        });
        dialog.show()
	},
	
	get_item_mr: async function (frm){
	    const allowed_request_types = [
        			"Material Issue",
		];
		var r = await lestari.utils.map_current_doc({
			method: "lestari.custom_function.make_stock_entry",
			source_doctype: "Material Request",
			target: me.frm,
			date_field: "transaction_date",
			setters: [
				{
					fieldtype: "Data",
					label: __("ID Material Request"),
					fieldname: "idmaterial_request",
				},
				{
					fieldtype: "Select",
					label: __("Purpose"),
					options: allowed_request_types.join("\n"),
					fieldname: "material_request_type",
					default: "Material Issue",
					mandatory: 1,
				},
				{
					label: __("Departmnent"),
					fieldname: "department",
					fieldtype: "Link",
					options: "Department",
					default: me.frm.doc.department || undefined,
					// change() {
					// 	setTimeout(function(){
				    //     	r.dialog.fields_dict.allow_child_item_selection.$input.click();
			        // 	},1000)
			        // 	if($(":input[data-fieldname='allow_child_item_selection']").is(':checked')){
            		// 	  setTimeout(function(){
            		// 		r.dialog.fields_dict.allow_child_item_selection.$input.click();
            		// 	  }, 2000)
            		// 	}
					// },
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
			   material_request_type: ["in", allowed_request_types],
			   status: ["not in", ["Transferred", "Issued", "Cancelled", "Stopped"]],
		   },
        //    add_filters_group: true,
        //    filter_group:[["Material Request Item","ordered_qty","<","qty"]],
		   allow_child_item_selection: true,
		   child_fieldname: "items",
		   child_columns: [
		   "item_code",
		   "description",
           "schedule_date",
		   "qty",
           "uom",
		   "ordinal",	
		   "warehouse",	
		   "ordered_qty",
		   ],
		  // get_query: function () {
				// 		var filters = {
				// 			docstatus: 1,
			 //               material_request_type: ["in", allowed_request_types],
			 //               status: ["not in", ["Transferred", "Issued", "Cancelled", "Stopped"]],
				// 		};
				// // 		if (me.frm.doc.customer) filters["customer"] = me.frm.doc.customer;
				// 		return {
				// 			query: "lestari.custom_function.get_material_requests_to_be_ordered",
				// 			filters: filters,
				// 		};
				// 	},
	    });
		  $(document).on("frappe.ui.Dialog:shown", function() {
			// Your custom logic here, e.g., perform some action when the dialog is shown
			if(!r.dialog.fields_dict['allow_child_item_selection'].get_value()){
				// r.dialog.fields_dict.allow_child_item_selection.$input.click()
				// r.dialog.fields_dict.department.$input.val(cur_frm.doc.department)
				setTimeout(function(){
					r.dialog.fields_dict.allow_child_item_selection.$input.click();
				},1000)
			}
	  
			/*if($(":input[data-fieldname='allow_child_item_selection']").is(':checked')){
			  setTimeout(function(){
				console.log(r)
				// $(":input[data-name='Warehouse']").val(cur_frm.doc.department);
				// console.log(r.child_datatable.columnmanager.applyFilter(r.child_datatable.columnmanager.getAppliedFilters())) 
			  }, 2000)
			}*/
		});
	}
});

frappe.ui.form.on('Stock Entry Detail', {
    items_add: function(frm, cdt, cdn) {
        set_row_numbers(frm);
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