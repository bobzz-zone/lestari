frappe.pages['user-roleperm-list'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'User Role Pemission List',
			single_column: true
		});
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
		$("#dataGrid").dxDataGrid({
			dataSource: employees.message,
        	keyExpr: 'user',
			showBorders: true,
			height: '30%',
			allowColumnReordering: true,
			allowColumnResizing: true,
			loadPanel:{
				enabled:true
			},
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
                allowedPageSizes: [10, 25, 50, 100],
                showPageSizeSelector: true,
                showNavigationButtons: true
            },
            paging: {
                pageSize: 25,
            },
			grouping:{
				autoExpandAll: false
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
			onExporting(e) {
				const workbook = new ExcelJS.Workbook();
				const worksheet = workbook.addWorksheet('Employees');
			
				DevExpress.excelExporter.exportDataGrid({
					component: e.component,
					worksheet,
					autoFilterEnabled: true,
				}).then(() => {
					workbook.xlsx.writeBuffer().then((buffer) => {
					saveAs(new Blob([buffer], { type: 'application/octet-stream' }), 'UserRolePermission.xlsx');
					});
				});
				e.cancel = true;
			},
		});
		
	},
	employees: function(){
		var data = frappe.call({
			method: 'lestari.lestari.page.user_roleperm_list.user_roleperm_list.contoh_report',
			args: {
				'doctype': 'User',
			}
		});

		return data
	},
})