frappe.pages['spk-ppic-list'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'SPK PPIC',
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
        	keyExpr: 'name',
			showBorders: true,
			allowColumnReordering: true,
			allowColumnResizing: true,
			columnsAutoWidth: true,
			columnAutoWidth: true,
			scrolling: {
				columnRenderingMode: 'virtual',
			  },
			groupPanel: {
				visible: true,
			},
			grouping:{
				autoExpandAll: false
			},
			selection: {
				mode: "multiple",
				allowSelectAll: true,
				selectAllMode: 'page' // or "multiple" | "none"
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
			//   }],
			// ,{
			},{
				dataField: 'name',
				format: 'string',
				alignment: 'left',
				// width: 110,
				caption: 'No FM'			   
			  }
			  ,{
				dataField: 'posting_date',
				format: 'date',
				alignment: 'right',
				caption: 'Posting Date',
				// width: 110,
				
			  },{
				dataField: 'urut_fm',
				format: 'string',
				alignment: 'left',
				// width: 110,
				caption: 'Urut FM'			   
			  },			   
			  {
				dataField: 'sub_kategori',
				format: 'string',
				// width: 150,
				caption: 'Sub Kategori'
			  },
			  {
				dataField: 'model',
				format: 'string',
				// width: 150,
				caption: 'No Model'
			  },
			  {
				dataField: 'kadar',
				format: 'string',
				// width: 150,
				caption: 'Kadar'
			  },
			  {
				dataField: 'qty',
				format: 'decimal',
				caption: 'Qty'
			  },
			  {
				dataField: 'berat',
				format: 'decimal',
				caption: 'Berat'
			  },
			  ],
			summary: {
				groupItems: [{
					column: 'no',
					summaryType: 'count',
					displayFormat: '{0} orders',
				  }, {
					column: 'qty',
					summaryType: 'sum',
					displayFormat: 'Total: {0}',
					showInGroupFooter: true,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 2,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  }],
			  },
			  onSelectionChanged(selectedItems) {
				const data = selectedItems.selectedRowsData;
				if (data.length > 0) {
				  $('#selected-items-container').text(
					data
					  .map((value) => `${value.FirstName} ${value.LastName}`)
					  .join(', '),
				  );
				} else {
				  $('#selected-items-container').text('Nobody has been selected');
				}
				if (!changedBySelectBox) {
				  titleSelectBox.option('value', null);
				}
		  
				changedBySelectBox = false;
				clearSelectionButton.option('disabled', !data.length);
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
					saveAs(new Blob([buffer], { type: 'application/octet-stream' }), 'TransferSalesman.xlsx');
				  });
				});
				e.cancel = true;
			  }
		});
		
	},
	employees: function(){
		var data = frappe.call({
			method: 'lestari.lestari.page.spk_ppic_list.spk_ppic_list.contoh_report',
			args: {
				'doctype': 'Purchase Order',
			}
		});

		return data
	},

})