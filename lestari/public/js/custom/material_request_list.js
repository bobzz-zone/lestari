frappe.listview_settings['Material Request'] = {

	button: {
        show: function(doc) {
            return true;
        },
        get_label: function() {
            return __('View Item');
        },
        get_description: function(doc) {
            return __('Print {0}', [doc.name])
        },
        action: function(doc) {
            console.log(doc.name)
            
             frappe.db.get_list('Material Request Item', {
                fields: ['name', 'item_code', 'item_name', 'idproduct', 'description', 'qty', 'uom', 'proses'],
                filters: {
                    parent: ['=', doc.name]
                },
                limit: null
            }).then(function(mr) {
                var hidden = 0
                console.log(mr)
                let d = new frappe.ui.Dialog({
                    title: 'Material Request Items',
                    fields: [
                    {
                        label: 'Name',
                        fieldname: 'name',
                        fieldtype: 'Data',
                        read_only: 1,
                        default:doc.name
                    },   
                    {
                        label: 'Details',
                        fieldname: 'details',
                        fieldtype: 'Table',
                        read_only: 1,
                        cannot_add_rows: 1,
                        cannot_delete_rows: 1,
                        allow_on_grid_editing: 0,
                        in_place_edit: 0,
                        fields: [
                            {
                                label: 'Name',
                                fieldname: 'name',
                                fieldtype: 'Data',
                                hidden: 1,
                            },
                            {
                                label: 'Item Code',
                                fieldname: 'item_code',
                                fieldtype: 'Link',
                                options: "Item",
                                read_only: 1,
                                in_list_view: 1,
                                columns: 2
                            },
                            {
                                label: 'Item Name',
                                fieldname: 'item_name',
                                fieldtype: 'Data',
                                read_only: 1,
                                in_list_view: 1,
                                columns: 2
                            },
                            {
                                label: 'ID Product',
                                fieldname: 'idproduct',
                                fieldtype: 'Data',
                                read_only: 1,
                                in_list_view: 1,
                                columns: 1
                            },
                            {
                                label: 'Description',
                                fieldname: 'description',
                                fieldtype: 'Data',
                                in_list_view: 1,
                                columns: 2
                            },
                            {
                                label: 'Qty',
                                fieldname: 'qty',
                                fieldtype: 'Float',
                                in_list_view: 1,
                                columns: 1
                            },
                            {
                                label: 'UOM',
                                fieldname: 'uom',
                                fieldtype: 'Link',
                                options: "UOM",
                                in_list_view: 1,
                                columns: 1
                            },
                            {
                                label: 'Proses',
                                fieldname: 'proses',
                                fieldtype: 'Link',
                                options: "Operation Usage",
                                in_list_view: 1,
                                columns: 1
                            }
                        ],
                        data: mr
                    }, ],
                    size: 'extra-large', // small, large, extra-large 
                    primary_action_label: 'Close',
                    primary_action: function() {
                        d.hide();
                    },
                });
                d.show();
            })
            //frappe.set_route("/app/print/Invoice/" + doc.name);
            
            // var objWindowOpenResult = window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
            //   + "doctype=" + encodeURIComponent("Invoice")
            //   + "&name=" + encodeURIComponent(doc.name)
            //   + "&trigger_print=0"
            //   + "&format=invoice print format"
            //   + "&no_letterhead=0"
            //   + "&_lang=en"
            // ));
            // if(!objWindowOpenResult) {
            //   msgprint(__("Please set permission for pop-up windows in your browser!")); return;
            // }
        }
    },

	add_fields: ["material_request_type", "status", "per_ordered", "per_received", "per_requested","transfer_status"],
	get_indicator: function(doc) {
		var precision = frappe.defaults.get_default("float_precision");
		if (doc.status=="Stopped") {
			return [__("Stopped"), "red", "status,=,Stopped"];
		} else if (doc.transfer_status && doc.docstatus != 2) {
			if (doc.transfer_status == "Not Started") {
				return [__("Not Started"), "orange"];
			} else if (doc.transfer_status == "In Transit") {
				return [__("In Transit"), "yellow"];
			} else if (doc.transfer_status == "Completed") {
				return [__("Completed"), "green"];
			}
		} else if (doc.docstatus==1 && flt(doc.per_ordered, precision) == 0 && flt(doc.per_requested, precision) == 0) {
			return [__("Pending"), "orange", "per_ordered,=,0|per_requested,=,0"];
		}  else if (doc.docstatus==1 && doc.material_request_type == "Purchase" && flt(doc.per_requested, precision) < 100) {
			return [__("Partially requested"), "yellow", "per_requested,<,100"];
		}  else if (doc.docstatus==1 && flt(doc.per_ordered, precision) < 100 && flt(doc.per_requested, precision) < 100) {
			return [__("Partially ordered"), "yellow", "per_ordered,<,100"];
		} else if (doc.docstatus==1 && flt(doc.per_ordered, precision) == 100) {
			if (doc.material_request_type == "Purchase" && flt(doc.per_received, precision) < 100 && flt(doc.per_received, precision) > 0) {
				return [__("Partially Received"), "yellow", "per_received,<,100"];
			} else if (doc.material_request_type == "Purchase" && flt(doc.per_received, precision) == 100) {
				return [__("Received"), "green", "per_received,=,100"];
			} else if (doc.material_request_type == "Purchase") {
				return [__("Ordered"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Material Transfer") {
				return [__("Transfered"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Material Issue") {
				return [__("Issued"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Customer Provided") {
				return [__("Received"), "green", "per_ordered,=,100"];
			} else if (doc.material_request_type == "Manufacture") {
				return [__("Manufactured"), "green", "per_ordered,=,100"];
			}
		} else if (doc.docstatus==1 && doc.material_request_type == "Purchase" && flt(doc.per_requested, precision) == 100) {
            return [__("Requested"), "green", "per_requested,=,100"];
        }
	}
};
