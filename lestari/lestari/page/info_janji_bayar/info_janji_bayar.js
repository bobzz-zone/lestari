frappe.pages['info-janji-bayar'].on_page_load = function(wrapper) {
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
			title: 'Info Janji Bayar',
			single_column: true
		});
		this.page.set_secondary_action('Refresh', () => me.make(), { icon: 'refresh', size: 'sm'})
		this.posting_date = ""
		this.page.add_field({"fieldtype": "DateRange", "fieldname": "posting_date","default": [frappe.datetime.month_start(), frappe.datetime.now_date()],
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
		// console.log(this.page.wrapper.attr('id'))
		// DevExpress.localization.locale(navigator.language);
		let body = `<div class="dx-viewport">
			<div id="dataGrid_`+this.page.wrapper.attr('id')+`"></div>
		</div>`;
		$(frappe.render_template(body, this)).appendTo(this.page.main)
		var infojb = await this.infojb()
		$("#dataGrid_"+this.page.wrapper.attr('id')).dxDataGrid({
			dataSource: infojb.message,
        	keyExpr: 'janji_bayar',
			height: 650,
			width: '100%',
			// columnAutoWidth: true,
			allowColumnReordering: false,
			showBorders: true,
			hoverStateEnabled:true,
			preloadEnabled:true,
			renderAsync:true,
			filterBuilder: true,
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
				dataField: 'customer',
				width: 120,
				alignment: 'center',
				caption: 'Customer',
				groupIndex: 0
			},{
				dataField: 'tanggal_janji',
				width: 120,
				alignment: 'center',
				caption: 'Tanggal Janji',
				
			},{
				dataField: 'jenis_janji',
				width: 120,
				alignment: 'center',
				caption: 'Jenis Janji',
				
			},{
				dataField: 'status',
				width: 120,
				alignment: 'center',
				caption: 'Status',
				
			},{
				dataField: 'janji_bayar',
				width: 100,
				alignment: 'center',
				caption: 'Janji Bayar',
			},{
				dataField: 'total_janji_bayar',
				alignment: 'right',
				width: 150,
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'Total Janji Bayar'
			},{
				dataField: 'total_terbayar',
				alignment: 'right',
				width: 150,
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'Total Terbayar'
			},{
				dataField: 'sisa_janji',
				alignment: 'right',
				width: 150,
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
				caption: 'Sisa Janji'
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
					column: 'total_janji_bayar',
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
					column: 'total_janji_bayar',
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
					column: 'total_terbayar',
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
					column: 'total_terbayar',
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
					column: 'sisa_janji',
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
					column: 'sisa_janji',
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
				enabled:true,
      			template: masterDetailTemplate,
				// template: function (container, options){
				// 	console.log(container)
				// 	var currentEmployeeData = infojb.message[options.key - 1];
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
				const worksheet = workbook.addWorksheet('infojb');
		  
				DevExpress.excelExporter.exportDataGrid({
				  component: e.component,
				  worksheet,
				  autoFilterEnabled: true,
				}).then(() => {
				  workbook.xlsx.writeBuffer().then((buffer) => {
					saveAs(new Blob([buffer], { type: 'application/octet-stream' }), 'JanjiBayar.xlsx');
				  });
				});
				e.cancel = true;
			  }
		});
		function masterDetailTemplate(_, masterDetailOptions) {
			console.log(masterDetailOptions)
			return $('<div>').dxTabPanel({
				items: [{
					title: 'History',
					template: createInvoiceTabTemplate(masterDetailOptions.data.detail)
			  },
			//    {
			// 		title: 'Customer Deposit',
			// 		template: createAdvGoldTabTemplate(masterDetailOptions.data.customer_deposit),
			//   }
			],
			});
	  	}
		  function createInvoiceTabTemplate(masterDetailData) {
			  return function () {
				// console.log(masterDetailData)
				
				return $('<div>').addClass('form-container').dxForm({
				  labelLocation: 'top',
				  items: [{
					label: { text: 'Detail' },
					template: createOrderHistoryTemplate(masterDetailData),
				  }],
				});
			  };
		  }
		//   function createAdvGoldTabTemplate(masterDetailData) {
		// 	  return function () {
		// 		// console.log(masterDetailData)
				
		// 		return $('<div>').addClass('form-container').dxForm({
		// 		  labelLocation: 'top',
		// 		  items: [{
		// 			label: { text: 'Customer Deposit' },
		// 			template: createOrderHistoryTemplate(masterDetailData),
		// 		  }],
		// 		});
		// 	  };
		//   }
		 
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
	infojb: function(){
		var me = this
		var data = frappe.call({
			method: 'lestari.lestari.page.info_janji_bayar.info_janji_bayar.contoh_report',
			args: {
				'doctype': 'Gold Payment',
				'posting_date': me.posting_date,
			}
		});

		return data
	},

})