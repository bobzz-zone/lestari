frappe.pages['dev-extreme-report'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'DevExtreme',
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
		
		DevExpress.localization.locale('id');
		$("#dataGrid").dxDataGrid({
			dataSource: employees.message,
        	keyExpr: 'name',
			showBorders: true,
			allowColumnReordering: true,
			allowColumnResizing: true,
			groupPanel: {
				visible: true,
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
				dataField: 'name',
				format: 'string',
			  },
			  {
				dataField: 'supplier',
				format: 'string',
			  },
			  {
				dataField: 'total',
				alignment: 'right',
				format: {
					type: "currency",
					currency: "IDR"
				}
			  },
			  ],
			summary: {
				groupItems: [{
					column: 'no',
					summaryType: 'count',
					displayFormat: '{0} orders',
				  }, {
					column: 'total',
					summaryType: 'sum',
					displayFormat: 'Total: {0}',
					valueFormat: 'currency',
					showInGroupFooter: false,
					alignByColumn: true,
				  }],
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
			method: 'lestari.lestari.page.dev_extreme_report.dev_extreme_report.contoh_report',
			args: {
				'doctype': 'Purchase Order',
			}
		});

		return data
	},

})