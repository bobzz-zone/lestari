frappe.pages['report-pencocokan-pi'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Report Pencocokan Piutang',
			single_column: true
		});
		this.make()
	},
	// make page
	make: async function(){
		let me = $(this);
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
		console.log(employees)		
		// DevExpress.localization.locale('id');
		$("#dataGrid").dxDataGrid({
			dataSource: employees.message,
        	keyExpr: 'voucher_no',
			showBorders: true,
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
			filterRow: { visible: true },
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
			  },
			  {
				dataField: 'voucher_no',
				format: 'string',
				width: 150,
				caption: 'Voucher No'
			  },
			  {
				dataField: 'voucher_type',
				format: 'string',
				width: 150,
				caption: 'Voucher Type'
			  },
			  {
				  dataField: 'customer',
				  format: 'string',
				  width: 150,
				  caption: 'Customer',
				  groupIndex: 0
				},
			  {
				dataField: 'date',
				format: 'string',
				width: 150,
				caption: 'Posting Date'
			  },
			  {
				dataField: 'tutupan',
				format: 'decimal',
				caption: 'Tutupan'
			  },
			  {
				dataField: 'outstanding',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'Outstanding'
			  },
			  {
				dataField: 'deposit_gold',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'Deposit Gold'
			  },
			  {
				dataField: 'deposit_idr',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				  caption: 'Deposit IDR'
			  },
			  ],
			  sortByGroupSummaryInfo: [{
				summaryItem: 'count',
			  }],
			summary: {
				totalItems: [
				{
						column: 'outstanding',
						summaryType: 'sum',
						displayFormat: 'Outstanding: {0}',
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
					column: 'deposit_gold',
					summaryType: 'sum',
					displayFormat: 'Deposit Gold: {0}',
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
					column: 'Deposit IDR',
					summaryType: 'sum',
					displayFormat: 'Deposit IDR: {0}',
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
				groupItems: [{
					column: 'no',
					summaryType: 'count',
					displayFormat: '{0} orders',
					showInGroupFooter: false,
				  }, 
				  {
					column: 'outstanding',
					summaryType: 'sum',
					displayFormat: 'Outstanding: {0}',
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
					column: 'deposit_gold',
					summaryType: 'sum',
					displayFormat: 'Deposit Gold: {0}',
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
					column: 'Deposit IDR',
					summaryType: 'sum',
					displayFormat: 'Deposit IDR: {0}',
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
					saveAs(new Blob([buffer], { type: 'application/octet-stream' }), 'PurchaseOrder.xlsx');
				  });
				});
				e.cancel = true;
			  }
		});
	},
	employees: function(){
		var data = frappe.call({
			method: 'lestari.lestari.page.kartu_piutang_custom.kartu_piutang_custom.contoh_report',
			args: {
				'doctype': 'Purchase Order',
			}
		});

		return data
	},

})