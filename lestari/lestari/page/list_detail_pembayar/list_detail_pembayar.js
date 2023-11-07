frappe.pages['list-detail-pembayar'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		var me = this
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'List Detail Pembayaran',
			single_column: true
		});
		this.posting_date = ""
		this.page.add_field({"fieldtype": "DateRange", "fieldname": "posting_date","default": [frappe.datetime.month_start(), frappe.datetime.now_date()],
			"label": __("Posting Date"), "reqd": 1,
			change: function() {
				me.posting_date = this.value;
				me.make()
			}
		}),
		this.make()
	},
	// make page
	make: async function(){
		var me = this
		DevExpress.localization.locale(navigator.language);
		let body = `<div class="dx-viewport">
			<div id="dataGrid"></div>
		</div>`;
		$(frappe.render_template(body, this)).appendTo(this.page.main)
		var employees =  await this.employees()
		console.log(employees.message)		
		$("#dataGrid").dxDataGrid({
			dataSource: employees.message,
			// {
			// 	store:{
			// 		type: 'array',
			// 		key: 'no',
			// 		data: employees.message
			// 	}
			// },
        	keyExpr: 'no_nota',
			height: 780,
			width: '100%',
			// columnAutoWidth: true,
			allowColumnReordering: false,
			showBorders: true,
			summary: {
				groupItems: [{
					summaryType: "count"
				}]
			},
			columnFixing: {
				enabled: true,
				fixedPosition: "top"
			},
			scrolling: {
				mode: 'virtual',
				rowRenderingMode: 'virtual',
			},
			paging: {
				enabled: false
			},
			filterRow: {
				visible: true
			},
			headerFilter: {
				visible: true
			},
			filterRow: {
				visible: true
			},
			grouping: {  
				autoExpandAll: false  
			},  
			groupPanel: {
				visible: true
			},
			searchPanel: {
				visible: true
			},
			focusedRowEnabled: false,
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
				dataField: 'no_nota',
				width: 100,
				alignment: 'center',
				caption: 'No Nota',
			},{
				dataField: 'customer',
				width: 120,
				alignment: 'center',
				caption: 'Customer',
				groupIndex: 0
			},{
				dataField: 'posting_date',
				width: 100,
				alignment: 'center',
				caption: 'Tanggal Posting',
			},{
				dataField: 'item',
				width: 80,
				alignment: 'center',
				caption: 'Item',
			},{
				dataField: 'bruto',
				width: 100,
				dataType: 'decimal',
				alignment: 'right',
				caption: 'Bruto',
			},{
				dataField: 'rate',
				width: 100,
				dataType: 'decimal',
				alignment: 'right',
				caption: 'Rate',
			},{
				dataField: 'amount24k',
				width: 150,
				dataType: 'decimal',
				alignment: 'right',
				caption: '24K',
			},{
				dataField: 'mode_of_payment',
				width: 100,
				dataType: 'string',
				alignment: 'left',
				caption: 'Pembayaran',
			},{
				dataField: 'amountidr',
				alignment: 'right',
				width: 150,
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'IDR'
			},{
				dataField: 'adv_gold',
				width: 100,
				dataType: 'string',
				alignment: 'center',
				caption: 'Adv Gold',
			},{
				dataField: 'gold_deposit',
				width: 150,
				dataType: 'decimal',
				alignment: 'right',
				caption: 'Gold Deposit',
			},{
				dataField: 'gold_allocated',
				width: 150,
				dataType: 'decimal',
				alignment: 'right',
				caption: 'Allocated',
			},{
				dataField: 'adv_idr',
				width: 100,
				dataType: 'string',
				alignment: 'center',
				caption: 'Adv IDR',
			},{
				dataField: 'idr_deposit',
				alignment: 'right',
				width:150,
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'IDR Deposit'
			},{
				dataField: 'idr_allocated',
				alignment: 'right',
				width:150,
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'Allocated'
			},{
				dataField: 'sales_bundle',
				width: 100,
				alignment: 'center',
				caption: 'Bundle',
			},{
				dataField: 'no_invoice',
				width: 'auto',
				alignment: 'right',
				caption: 'Invoice',
			}
		],
		summary:{
			groupItems: [
				{
					column: 'no',
					summaryType: 'count',
					displayFormat: '{0} Nota',
				},
				{
					column: 'amount24k',
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
					column: 'amountidr',
					summaryType: 'sum',
					displayFormat: 'Total IDR: {0}',
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
					column: 'amount24k',
					summaryType: 'sum',
					displayFormat: 'Total 24K: {0}',
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
					column: 'amountidr',
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
					column: 'gold_allocated',
					summaryType: 'sum',
					displayFormat: 'Adv Gold : {0}',
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
			]
		},
			masterDetail:{
				enabled:false,
      			template: masterDetailTemplate,
				// template: function (container, options){
				// 	console.log(container)
				// 	var currentEmployeeData = employees.message[options.key - 1];
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
				const worksheet = workbook.addWorksheet('Employees');
		  
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
	employees: function(){
		var me = this
		var data = frappe.call({
			method: 'lestari.lestari.page.list_detail_pembayar.list_detail_pembayar.contoh_report',
			args: {
				'doctype': 'Gold Payment',
				'posting_date': me.posting_date,
			}
		});

		return data
	},

})