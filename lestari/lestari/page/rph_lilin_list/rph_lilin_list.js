frappe.pages['rph-lilin-list'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		var me = this
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'RPH Lilin',
			single_column: true
		});
		this.list_spk = []
		this.posting_date = ""
		// this.page.add_inner_button('Update Posts', () => update_posts())
		// this.page.change_inner_button_type('Update Posts', null, 'primary');
		this.page.set_primary_action('Buat SPK PRODUKSI', () => this.submit(), { icon: 'add', size: 'sm'})
		this.page.set_secondary_action('Refresh', () => this.make(), { icon: 'refresh', size: 'sm'})
		this.page.add_inner_button('List SPK PRODUKSI', () => frappe.set_route(['List', 'SPK Produksi']))
		this.page.add_field({"fieldtype": "Data", "fieldname": "cari",
			"label": __("Cari"),
			change: function() {
				me.posting_date = this.value;
			}
		}),
		this.page.add_field({"fieldtype": "Select", "fieldname": "jenis","option":"",
			"label": __("Cari"),
			change: function() {
				me.posting_date = this.value;
			}
		}),
		this.page.add_field({"fieldtype": "Date", "fieldname": "posting_date","default": "Today",
			"label": __("Posting Date"), "reqd": 1,
			change: function() {
				me.posting_date = this.value;
			}
		}),
		this.page.add_select(__("Document Type"),
				[{ value: "", label: __("Select Document Type") + "..." }].concat(this.options.doctypes))
				.change(function () {
					frappe.set_route("permission-manager", $(this).val());
				});

		// this.page.set_secondary_action(
		// 	__('Buat SPK Produksi'),
		// 	() => this.show_user_search_dialog(),
		// 	{ icon: 'add', size: 'sm'}
		// );
		this.make();
	},
	// make page
	make: async function(){
		let me = this
		DevExpress.localization.locale(navigator.language);
		let body = `<div class="dx-viewport">
			<div id="dataGrid"></div>

		</div>`;
		$(frappe.render_template(body, this)).appendTo(this.page.main)
		var spk_ppic =  await this.spk_ppic()
		// var formattedNumber = DevExpress.localization.formatNumber(spk_ppic.message., {
		// 	style: "currency",
		// 	currency: "",
		// 	useGrouping: true
		//   });
		// console.log(spk_ppic)		
		// DevExpress.localization.locale('id');
		$("#dataGrid").dxDataGrid({
			dataSource: spk_ppic.message,
        	keyExpr: 'name',
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
				autoExpandAll: false
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
				sortOrder: 'asc',
				// width: 110,
				
			  },{
				dataField: 'urut_fm',
				format: 'string',
				alignment: 'left',
				// width: 110,
				caption: 'Urut FM',
				allowHeaderFiltering: false,			   
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
				caption: 'Qty',
				allowHeaderFiltering: false,
			  },
			  {
				dataField: 'berat',
				format: 'decimal',
				caption: 'Berat',
				allowHeaderFiltering: false,
			  },
			  ],
			  onSelectionChanged(e) {
				e.component.refresh(true);
				if(e.currentSelectedRowKeys[0] != null){	
					me.list_spk.push(e.currentSelectedRowKeys[0])
				}
				if(e.currentDeselectedRowKeys[0] != null){
					me.list_spk = me.list_spk.filter(data => data != e.currentDeselectedRowKeys[0])
				}
				// console.log(e)
				// console.log(me.list_spk)
			  },
			  summary: {
				totalItems: [{
				  name: 'SelectedRowsSummary',
				  showInColumn: 'qty',
				  displayFormat: 'Qty: {0}',
				  summaryType: 'custom',
				},
				],
				calculateCustomSummary(options) {
					
				  if (options.name === 'SelectedRowsSummary') {
					if (options.summaryProcess === 'start') {
					  options.totalValue = 0;
					}
					if (options.summaryProcess === 'calculate') {
					  if (options.component.isRowSelected(options.value.name)) {
						options.totalValue += options.value.qty;
					  }
					}
				  }
				},
			  },
			  onExporting(e) {
				const workbook = new ExcelJS.Workbook();
				const worksheet = workbook.addWorksheet('spk_ppic');
		  
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
	spk_ppic: function(){
		var data = frappe.call({
			method: 'lestari.lestari.page.rph_lilin_list.rph_lilin_list.get_spk_ppic_list',
			args: {
				'doctype': 'SPK Produksi',
			}
		});

		return data
	},
	submit: function(){
		var me = this
		// console.log("test"+me.posting_date) // disini keluar test doang masih kosong
		frappe.call({
			method: 'lestari.lestari.page.rph_lilin_list.rph_lilin_list.make_spk_ppic',
			args: {
				'data': this.list_spk,
				'posting_date': me.posting_date // disini kosong why???
			},
			callback: function(){
				me.make()
			}
		})
	}
})