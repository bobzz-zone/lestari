frappe.pages['info-proses-penjuala'].on_page_load = function(wrapper) {
	var tema = frappe.boot.user.desk_theme
		if(tema == "Dark"){
			frappe.require('/assets/lestari/css/dx.dark.css',function() {
				new DevExtreme(wrapper)
			})
		}else{
			frappe.require('/assets/lestari/css/dx.light.css',function() {
				new DevExtreme(wrapper)
			})
		}
		DevExpress.viz.refreshTheme();
	frappe.breadcrumbs.add("Gold Selling");
}
DevExtreme = Class.extend({
	init: function(wrapper){
		var me = this
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Info Proses Penjualan',
			single_column: true
		});
		this.page.set_secondary_action('Refresh', () => me.make(), { icon: 'refresh', size: 'sm'})
		this.posting_date = ""
		this.page.add_field({"fieldtype": "DateRange", "fieldname": "posting_date","default": ['2023-10-31', frappe.datetime.now_date()],
			"label": __("Posting Date"), "reqd": 1,
			change: function() {
				me.posting_date = this.value;
				me.make()
			}
		}),
		this.make()
		// frappe.msgprint('Data Terload')
	},
	// make page
	make: async function(){
		let me = this
		console.log(this.page.wrapper.attr('id'))
		// DevExpress.localization.locale(navigator.language);
		let body = `<div class="dx-viewport">
			<div id="dataGrid_`+this.page.wrapper.attr('id')+`"></div>
		</div>`;
		$(frappe.render_template(body, this)).appendTo(this.page.main)
		var infoproses = await this.infoproses()
		$("#dataGrid_"+this.page.wrapper.attr('id')).dxDataGrid({
			dataSource: infoproses.message,
        	keyExpr: 'no_nota',
			// height: 650,
			// width: '100%',
			// columnAutoWidth: true,
			// allowColumnReordering: false,
			// showBorders: true,
			// hoverStateEnabled:true,
			// preloadEnabled:true,
			// renderAsync:true,
			// filterBuilder: true,
			// summary: {
			// 	groupItems: [{
			// 		summaryType: "count"
			// 	}]
			// },
			// columnFixing: {
			// 	enabled: true,
			// 	fixedPosition: "top"
			// },
			// scrolling: {
			// 	mode: 'virtual',
			// 	rowRenderingMode: 'virtual',
			// },
			// paging: {
			// 	enabled: false
			// },
			// filterRow: {
			// 	visible: true
			// },
			// headerFilter: {
			// 	visible: true
			// },
			// filterRow: {
			// 	visible: true
			// },
			// grouping: {  
			// 	autoExpandAll: false  
			// },  
			// groupPanel: {
			// 	visible: true
			// },
			// searchPanel: {
			// 	visible: true
			// },
			// focusedRowEnabled: false,
			// export: {
			// 	enabled: true
			// },
			showBorders: true,
			rowAlternationEnabled: true,
			allowColumnReordering: true,
			allowColumnResizing: true,
			columnAutoWidth: true,
			scrolling: {
				columnRenderingMode: 'virtual',
			  },
			groupPanel: {
				visible: true,
			},
			grouping:{
				autoExpandAll: false,
			},
			paging: {
				pageSize: 25,
			},
			pager: {
			visible: true,
			allowedPageSizes: [25, 50, 100, 'all'],
			showPageSizeSelector: true,
			showInfo: true,
			showNavigationButtons: true,
			},
			filterRow: { visible: true, applyFilter: 'auto'},
			filterPanel: { visible: true },
        	searchPanel: { visible: true }, 
			columnChooser: { enabled: true },
			headerFilter: {
				visible: true,
			  },
			export: {
				enabled: true
			},
			columns:[
			{
				dataField: 'no',
				width: 50,
				alignment: 'center',
				caption: 'No.'
			},{
				dataField: 'customer',
				width: 120,
				alignment: 'center',
				caption: 'Customer',
				groupIndex: 0
			},{
				dataField: 'subcustomer',
				width: 120,
				alignment: 'center',
				caption: 'SubCustomer',
				
			},{
				dataField: 'no_nota',
				width: 100,
				alignment: 'center',
				caption: 'No Nota',
			},{
				dataField: 'posting_date',
				width: 100,
				alignment: 'center',
				caption: 'Tanggal Posting',
			},{
				dataField: 'sales',
				width: 120,
				alignment: 'center',
				caption: 'Sales',
			},{
				dataField: 'bundle',
				width: 150,
				alignment: 'center',
				caption: 'Bundle',
			},{
				dataField: 'berat_kotor',
				width: 150,
				dataType: 'decimal',
				alignment: 'right',
				caption: 'Berah Kotor',
			},{
				dataField: 'berat_bersih',
				width: 150,
				dataType: 'decimal',
				alignment: 'right',
				caption: 'Berat Bersih',
			},{
				dataField: 'satuan',
				width: 80,
				dataType: 'decimal',
				alignment: 'right',
				caption: 'Satuan',
			},{
				dataField: 'tutupan',
				alignment: 'right',
				width: 150,
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'Tutupan'
			},{
				dataField: 'tax_status',
				width: 100,
				alignment: 'center',
				caption: 'Tax',
			},{
				dataField: 'ppn',
				alignment: 'right',
				width: 150,
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'PPN'
			},{
				dataField: 'pph',
				alignment: 'right',
				width: 150,
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'PPH'
			},{
				dataField: 'user',
				width: 150,
				alignment: 'center',
				caption: 'User',
			}	
		],
		summary:{
			totalItems: [
				{
					column: 'berat_kotor',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 2,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
			},{
				column: 'berat_bersih',
				summaryType: 'sum',
				displayFormat: '{0}',
				showInGroupFooter: false,
				alignByColumn: true,
				valueFormat: {
					type: 'fixedPoint',
					precision: 2,
					thousandsSeparator: ',',
					currencySymbol: '',
					useGrouping: true,
				},
		},
			],
			groupItems: [
				{
					column: 'no',
					summaryType: 'count',
					displayFormat: '{0} Nota',
				},
				{
					column: 'berat_kotor',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: true,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 2,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				},
				{
					column: 'berat_kotor',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 2,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				},
				{
					column: 'berat_bersih',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 2,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				},
				{
					column: 'berat_bersih',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: true,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 2,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				}
			]
		},
			masterDetail:{
				enabled:false,
      			template: masterDetailTemplate,
				// template: function (container, options){
				// 	console.log(container)
				// 	var currentEmployeeData = infoproses.message[options.key - 1];
				// 	container.addClass("internal-grid-container");
				// 	$("<div>")
				// 	.addClass("internal-grid")
				// 	.dxDataGrid({
				// 		dataSource: currentEmployeeData.inv
				// 	})
				// 	.appendTo(container)
				// }
			},
			onExporting(e) {
				const workbook = new ExcelJS.Workbook();
				const worksheet = workbook.addWorksheet('infoproses');
		  
				DevExpress.excelExporter.exportDataGrid({
				  component: e.component,
				  worksheet,
				  autoFilterEnabled: true,
				}).then(() => {
				  workbook.xlsx.writeBuffer().then((buffer) => {
					saveAs(new Blob([buffer], { type: 'application/octet-stream' }), 'Pembayaran.xlsx');
				  });
				});
				e.cancel = true;
			  }
		});
		function masterDetailTemplate(_, masterDetailOptions) {
			// console.log(masterDetailOptions)
			return $('<div>').dxTabPanel({
				items: [{
					title: 'Gold Invoice',
					template: createInvoiceTabTemplate(masterDetailOptions.data.inv)
			  }, {
					title: 'Advance Gold',
					template: createAdvGoldTabTemplate(masterDetailOptions.data.adv_gold),
			  }, {
					title: 'Advance IDR',
					template: createAdvIDRTabTemplate(masterDetailOptions.data.adv_idr),
				}, {
					title: 'Stock Payment',				
					template: createStockPaymentTabTemplate(masterDetailOptions.data.stock_payment),
				}, {
					title: 'IDR Payment',
					template: createIDRPaymentTabTemplate(masterDetailOptions.data.idr_payment),
			  }],
			});
	  	}
		  function createInvoiceTabTemplate(masterDetailData) {
			  return function () {
				// console.log(masterDetailData)
				
				return $('<div>').addClass('form-container').dxForm({
				  labelLocation: 'top',
				  items: [{
					label: { text: 'Gold Invoice' },
					template: createOrderHistoryTemplate(masterDetailData),
				  }],
				});
			  };
		  }
		  function createAdvGoldTabTemplate(masterDetailData) {
			  return function () {
				// console.log(masterDetailData)
				
				return $('<div>').addClass('form-container').dxForm({
				  labelLocation: 'top',
				  items: [{
					label: { text: 'Advance Gold' },
					template: createOrderHistoryTemplate(masterDetailData),
				  }],
				});
			  };
		  }
		  function createAdvIDRTabTemplate(masterDetailData) {
			  return function () {
				// console.log(masterDetailData)
				
				return $('<div>').addClass('form-container').dxForm({
				  labelLocation: 'top',
				  items: [{
					label: { text: 'Advance IDR' },
					template: createOrderHistoryTemplate(masterDetailData),
				  }],
				});
			  };
		  }
		  function createStockPaymentTabTemplate(masterDetailData) {
			  return function () {
				// console.log(masterDetailData)
				
				return $('<div>').addClass('form-container').dxForm({
				  labelLocation: 'top',
				  items: [{
					label: { text: 'Stock Payment' },
					template: createOrderHistoryTemplate(masterDetailData),
				  }],
				});
			  };
		  }
		  function createIDRPaymentTabTemplate(masterDetailData) {
			  return function () {
				// console.log(masterDetailData)
				
				return $('<div>').addClass('form-container').dxForm({
				  labelLocation: 'top',
				  items: [{
					label: { text: 'IDR Payment' },
					template: createOrderHistoryTemplate(masterDetailData),
				  }],
				});
			  };
		  }
		  function createOrderHistoryTemplate(masterDetailData) {
			// console.log(masterDetailData)
			return function () {
			  return $('<div>').dxDataGrid({
				dataSource: masterDetailData,
				height: 250,
				paging: {
					enabled: false
				},
				scrolling: {
					mode: 'virtual',
					rowRenderingMode: 'virtual',
				},
				showBorders: true,
			  });
			};
		  }
	},
	infoproses: function(){
		var me = this
		var data = frappe.call({
			method: 'lestari.lestari.page.info_proses_penjuala.info_proses_penjuala.contoh_report',
			args: {
				'doctype': 'Gold Payment',
				'posting_date': me.posting_date,
			}
		});

		return data
	},

})