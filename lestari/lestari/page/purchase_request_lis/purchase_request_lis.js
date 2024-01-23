frappe.pages['purchase-request-lis'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		var me = this
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Purchase Order',
			single_column: true
		});
		this.list_po = []
		this.supplier = ""
		this.tujuan = ""
		this.pajak = ""
		this.ppn = ""
		this.no_faktur = ""
		this.submitted = ""
		this.combine = ""
		// this.page.add_inner_button('Update Posts', () => update_posts())
		// this.page.change_inner_button_type('Update Posts', null, 'primary');
		this.page.set_primary_action('Buat Purchase Order', () => this.submit(), { icon: 'add', size: 'sm'})
		this.page.set_secondary_action('Refresh', () => this.make(), { icon: 'refresh', size: 'sm'})
		this.page.add_inner_button('List Purchase Order', () => frappe.set_route(['List', 'Purchase Order']))
		this.page.add_field({"fieldtype": "Select", "fieldname": "tujuan","options": ['','Non Logam','Logam','Batu'],
			"label": __("Tujuan"), "reqd": 0,
			change: function() {
				me.tujuan = this.value;
			}
		}),
		this.page.add_field({"fieldtype": "Link", "fieldname": "supplier","options": "Supplier",
			"label": __("Supplier"), "reqd": 1,
			change: function() {
				me.supplier = this.value;
			}
		}),
		this.page.add_field({"fieldtype": "Check", "fieldname": "combine","default": 0,
			"label": __("Combine PO"), "reqd": 0,
			change: function() {
				me.combine = this.value;
			}
		}),
		this.page.add_field({"fieldtype": "Check", "fieldname": "pajak","default": 0,
			"label": __("Pajak"), "reqd": 0,
			change: function() {
				me.pajak = this.value;
			}
		}),
		this.page.add_field({"fieldtype": "Check", "fieldname": "ppn","default": 0,
			"label": __("PPn"), "reqd": 0,
			change: function() {
				me.ppn = this.value;
			}
		}),
		this.page.add_field({"fieldtype": "Data", "fieldname": "no_faktur","default": "",
			"label": __("No Faktur"), "reqd": 0,
			change: function() {
				me.no_faktur = this.value;
			}
		}),
		this.page.add_field({"fieldtype": "Check", "fieldname": "submitted","default": 0,
			"label": __("Submit"), "reqd": 0,
			change: function() {
				me.submitted = this.value;
			}
		}),
		$(".awesomplete>ul").css("z-index","3");
		// this.page.set_secondary_action(
		// 	__('Buat SPK Produksi'),
		// 	() => this.show_user_search_dialog(),
		// 	{ icon: 'add', size: 'sm'}
		// );
		this.make()
	},
	// make page
	make: async function(){
		let me = this
		DevExpress.localization.locale(navigator.language);
		let body = `<div class="dx-viewport">
			<div id="dataGrid"></div>
		</div>`;
		$(frappe.render_template(body, this)).appendTo(this.page.main)
		var employees =  await this.employees()
		// var formattedNumber = DevExpress.localization.formatNumber(employees.message., {
		// 	style: "currency",
		// 	currency: "",
		// 	useGrouping: true
		//   });
		// console.log(employees)		
		// DevExpress.localization.locale('id');
		$("#dataGrid").dxDataGrid({
			dataSource: employees.message,
        	keyExpr: 'idm',
			showBorders: true,
			
			allowColumnReordering: true,
			allowColumnResizing: true,
			columnAutoWidth: true,
			columnFixing: {
                enabled: true,
                 fixedPosition: "top"
            },
			scrolling: {
				columnRenderingMode: 'virtual',
				// mode: 'infinite'
			  },
			groupPanel: {
				visible: true,
			},
			 pager: {
                allowedPageSizes: [25, 50, 100],
                showPageSizeSelector: true,
                showNavigationButtons: true
            },
            paging: {
                pageSize: 25,
            },
			grouping:{
				autoExpandAll: true
			},
			selection: {
				mode: "multiple",
				allowSelectAll: true,
				selectAllMode: 'page' // or "multiple" | "none"
			}, 
			filterRow: { visible: true },
			headerFilter: {
				visible: true,
			  },
        	searchPanel: { visible: true }, 
			columnChooser: { enabled: true },
			export: {
				enabled: true
			},
			columns: [{
				dataField: 'no',
				width: 50,
				alignment: 'center',
				caption: 'No.',
				allowHeaderFiltering: false,
				sortOrder: 'asc',
			//   }],
			// ,{
			},{
				dataField: 'no_mr',
				format: 'string',
				alignment: 'left',
				sortOrder: 'asc',
				// width: 110,
				caption: 'No MR',
				groupIndex: 0
	   
			  }
			,{
				dataField: 'idmaterial_request',
				format: 'string',
				alignment: 'left',
				// width: 110,
				caption: 'ID MR'			   
			  }
			  ,{
				dataField: 'transaction_date',
				format: 'date',
				alignment: 'right',
				caption: 'Posting Date',
				// sortOrder: 'asc',
				// width: 110,
				
			  },
			//   {
				// dataField: 'schedule_date',
				// format: 'date',
				// alignment: 'right',
				// caption: 'Required Date',
				// sortOrder: 'asc',
				// width: 110,
				
			//   },
			//   {
			// 	dataField: 'status',
			// 	format: 'string',
			// 	alignment: 'left',
			// 	// width: 110,
			// 	caption: 'Status',
			// 	allowHeaderFiltering: false,			   
			//   },
			  {
				dataField: 'employee_name',
				format: 'string',
				alignment: 'left',
				// width: 110,
				caption: 'Employee Name',
				// allowHeaderFiltering: false,			   
			  },{
				dataField: 'department',
				format: 'string',
				alignment: 'left',
				// width: 110,
				caption: 'Department',
				// allowHeaderFiltering: false,			   
			  },			   
			  {
				dataField: 'item_code',
				format: 'string',
				// width: 150,
				caption: 'Item Code'
			  },
			  {
				dataField: 'description',
				format: 'string',
				// width: 150,
				caption: 'Description'
			  },
			  {
				dataField: 'qty',
				format: 'decimal',
				caption: 'Qty',
				allowHeaderFiltering: false,
			  },
			  {
				dataField: 'ordered_qty',
				format: 'decimal',
				caption: 'Ordered Qty',
				allowHeaderFiltering: false,
			  },{
				dataField: 'idm',
				format: 'string',
				alignment: 'left',
				// width: 110,
				caption: 'IDM',
				// groupIndex: 0
	   
			  }
			  ],
			  onSelectionChanged(e) {
				e.component.refresh(true);
				if(e.currentSelectedRowKeys[0] != null){	
					me.list_po.push(e.currentSelectedRowKeys[0])
				}
				if(e.currentDeselectedRowKeys[0] != null){
					me.list_po = me.list_po.filter(data => data != e.currentDeselectedRowKeys[0])
				}
				// console.log(e)
				// console.log(me.list_spk)
			  },
			//   summary: {
			// 	totalItems: [{
			// 	  name: 'SelectedRowsSummary',
			// 	  showInColumn: 'qty',
			// 	  displayFormat: 'Qty: {0}',
			// 	  summaryType: 'custom',
			// 	},
			// 	],
			// 	calculateCustomSummary(options) {
					
			// 	  if (options.name === 'SelectedRowsSummary') {
			// 		if (options.summaryProcess === 'start') {
			// 		  options.totalValue = 0;
			// 		}
			// 		if (options.summaryProcess === 'calculate') {
			// 		  if (options.component.isRowSelected(options.value.name)) {
			// 			options.totalValue += options.value.qty;
			// 		  }
			// 		}
			// 	  }
			// 	},
			//   },
			  onExporting(e) {
				const workbook = new ExcelJS.Workbook();
				const worksheet = workbook.addWorksheet('Employees');
		  
				DevExpress.excelExporter.exportDataGrid({
				  component: e.component,
				  worksheet,
				  autoFilterEnabled: true,
				}).then(() => {
				  workbook.xlsx.writeBuffer().then((buffer) => {
					saveAs(new Blob([buffer], { type: 'application/octet-stream' }), 'TransferSalesman.xlsx');
				  });
				});
				e.cancel = true;
			},
			// onSelectionChanged(selectedItems) {
            //     const data = selectedItems.selectedRowsData;
            //     if (data.length > 0) {
            //         // $('#selected-items-container').val(
            //         // data
            //         //     .map((value) => `${value.linkPopup}`)
            //         //     .join(', '),
            //         // );
			// 		console.log(data)
            //     } else {
            //         $('#selected-items-container').val('NULL');
                    
            //     }
       
            // },
		});
		
	},
	employees: function(){
		var data = frappe.call({
			method: 'lestari.lestari.page.purchase_request_lis.purchase_request_lis.contoh_report',
		});

		return data
	},
	submit: function(){
		var me = this
		// console.log("test"+me.supplier) // disini keluar test doang masih kosong
		frappe.call({
			method: 'lestari.lestari.page.purchase_request_lis.purchase_request_lis.make_po',
			args: {
				'data': this.list_po,
				'supplier': me.supplier, // disini kosong why???
				"tujuan":me.tujuan,
				"pajak":me.pajak,
				"ppn":me.ppn,
				"no_faktur":me.no_faktur,
				"submitted":me.submitted,
				"combine":me.combine
			},
			callback: function(){
				me.make()
			}
		})
	}
})