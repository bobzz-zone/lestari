frappe.pages['create-peta-oven'].on_page_load = function(wrapper) {
    new PetaOven(wrapper);
    frappe.breadcrumbs.add("Lestari");
}

PetaOven = Class.extend({
    init: function(wrapper) {
        var me = this;
        this.page = frappe.ui.make_app_page({
            parent: wrapper,
            title: 'Create Peta Oven',
            single_column: true,
            card_layout:true
        });

        // Create a container for fields and content
        let body = `
        <div id="peta-oven-fields"></div>
        <div id="datatable-container"></div>
        <div id="peta-oven-content" style="padding:2% !important;"></div>
    `;

        $(frappe.render_template(body, this)).appendTo(this.page.main)

        this.fieldsContainer = this.page.main.find('#peta-oven-fields');
        this.content = this.page.main.find('#peta-oven-content');
        this.datatableContainer = this.page.main.find('#datatable-container');

        this.posting_date = "";
        this.used = 1;
        
        this.setupFields();

        this.page.set_primary_action('Refresh', () => me.make(), { icon: 'refresh' });

        this.data = [{'spk_gips': 'SPK001',
            'pohon_id': 'TREE001',
            'Kadar': 'K001',
            'base_karet': 'BR001',
            'oven': 'Oven3'},
           {'spk_gips': 'SPK002',
            'pohon_id': 'TREE002',
            'Kadar': 'K002',
            'base_karet': 'BR002',
            'oven': 'Oven2'},
           {'spk_gips': 'SPK003',
            'pohon_id': 'TREE003',
            'Kadar': 'K003',
            'base_karet': 'BR003',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK004',
            'pohon_id': 'TREE004',
            'Kadar': 'K004',
            'base_karet': 'BR004',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK005',
            'pohon_id': 'TREE005',
            'Kadar': 'K005',
            'base_karet': 'BR005',
            'oven': 'Oven3'},
           {'spk_gips': 'SPK006',
            'pohon_id': 'TREE006',
            'Kadar': 'K006',
            'base_karet': 'BR006',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK007',
            'pohon_id': 'TREE007',
            'Kadar': 'K007',
            'base_karet': 'BR007',
            'oven': 'Oven2'},
           {'spk_gips': 'SPK008',
            'pohon_id': 'TREE008',
            'Kadar': 'K008',
            'base_karet': 'BR008',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK009',
            'pohon_id': 'TREE009',
            'Kadar': 'K009',
            'base_karet': 'BR009',
            'oven': 'Oven3'},
           {'spk_gips': 'SPK010',
            'pohon_id': 'TREE010',
            'Kadar': 'K010',
            'base_karet': 'BR010',
            'oven': 'Oven3'},
           {'spk_gips': 'SPK011',
            'pohon_id': 'TREE011',
            'Kadar': 'K011',
            'base_karet': 'BR011',
            'oven': 'Oven3'},
           {'spk_gips': 'SPK012',
            'pohon_id': 'TREE012',
            'Kadar': 'K012',
            'base_karet': 'BR012',
            'oven': 'Oven3'},
           {'spk_gips': 'SPK013',
            'pohon_id': 'TREE013',
            'Kadar': 'K013',
            'base_karet': 'BR013',
            'oven': 'Oven2'},
           {'spk_gips': 'SPK014',
            'pohon_id': 'TREE014',
            'Kadar': 'K014',
            'base_karet': 'BR014',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK015',
            'pohon_id': 'TREE015',
            'Kadar': 'K015',
            'base_karet': 'BR015',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK016',
            'pohon_id': 'TREE016',
            'Kadar': 'K016',
            'base_karet': 'BR016',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK017',
            'pohon_id': 'TREE017',
            'Kadar': 'K017',
            'base_karet': 'BR017',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK018',
            'pohon_id': 'TREE018',
            'Kadar': 'K018',
            'base_karet': 'BR018',
            'oven': 'Oven2'},
           {'spk_gips': 'SPK019',
            'pohon_id': 'TREE019',
            'Kadar': 'K019',
            'base_karet': 'BR019',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK020',
            'pohon_id': 'TREE020',
            'Kadar': 'K020',
            'base_karet': 'BR020',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK021',
            'pohon_id': 'TREE021',
            'Kadar': 'K021',
            'base_karet': 'BR021',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK022',
            'pohon_id': 'TREE022',
            'Kadar': 'K022',
            'base_karet': 'BR022',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK023',
            'pohon_id': 'TREE023',
            'Kadar': 'K023',
            'base_karet': 'BR023',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK024',
            'pohon_id': 'TREE024',
            'Kadar': 'K024',
            'base_karet': 'BR024',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK025',
            'pohon_id': 'TREE025',
            'Kadar': 'K025',
            'base_karet': 'BR025',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK026',
            'pohon_id': 'TREE026',
            'Kadar': 'K026',
            'base_karet': 'BR026',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK027',
            'pohon_id': 'TREE027',
            'Kadar': 'K027',
            'base_karet': 'BR027',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK028',
            'pohon_id': 'TREE028',
            'Kadar': 'K028',
            'base_karet': 'BR028',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK029',
            'pohon_id': 'TREE029',
            'Kadar': 'K029',
            'base_karet': 'BR029',
            'oven': 'Oven3'},
           {'spk_gips': 'SPK030',
            'pohon_id': 'TREE030',
            'Kadar': 'K030',
            'base_karet': 'BR030',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK031',
            'pohon_id': 'TREE031',
            'Kadar': 'K031',
            'base_karet': 'BR031',
            'oven': 'Oven2'},
           {'spk_gips': 'SPK032',
            'pohon_id': 'TREE032',
            'Kadar': 'K032',
            'base_karet': 'BR032',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK033',
            'pohon_id': 'TREE033',
            'Kadar': 'K033',
            'base_karet': 'BR033',
            'oven': 'Oven3'},
           {'spk_gips': 'SPK034',
            'pohon_id': 'TREE034',
            'Kadar': 'K034',
            'base_karet': 'BR034',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK035',
            'pohon_id': 'TREE035',
            'Kadar': 'K035',
            'base_karet': 'BR035',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK036',
            'pohon_id': 'TREE036',
            'Kadar': 'K036',
            'base_karet': 'BR036',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK037',
            'pohon_id': 'TREE037',
            'Kadar': 'K037',
            'base_karet': 'BR037',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK038',
            'pohon_id': 'TREE038',
            'Kadar': 'K038',
            'base_karet': 'BR038',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK039',
            'pohon_id': 'TREE039',
            'Kadar': 'K039',
            'base_karet': 'BR039',
            'oven': 'Oven2'},
           {'spk_gips': 'SPK040',
            'pohon_id': 'TREE040',
            'Kadar': 'K040',
            'base_karet': 'BR040',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK041',
            'pohon_id': 'TREE041',
            'Kadar': 'K041',
            'base_karet': 'BR041',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK042',
            'pohon_id': 'TREE042',
            'Kadar': 'K042',
            'base_karet': 'BR042',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK043',
            'pohon_id': 'TREE043',
            'Kadar': 'K043',
            'base_karet': 'BR043',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK044',
            'pohon_id': 'TREE044',
            'Kadar': 'K044',
            'base_karet': 'BR044',
            'oven': 'Oven1'},
           {'spk_gips': 'SPK045',
            'pohon_id': 'TREE045',
            'Kadar': 'K045',
            'base_karet': 'BR045',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK046',
            'pohon_id': 'TREE046',
            'Kadar': 'K046',
            'base_karet': 'BR046',
            'oven': 'Oven4'},
           {'spk_gips': 'SPK047',
            'pohon_id': 'TREE047',
            'Kadar': 'K047',
            'base_karet': 'BR047',
            'oven': 'Oven5'},
           {'spk_gips': 'SPK048',
            'pohon_id': 'TREE048',
            'Kadar': 'K048',
            'base_karet': 'BR048',
            'oven': 'Oven3'},
           {'spk_gips': 'SPK049',
            'pohon_id': 'TREE049',
            'Kadar': 'K049',
            'base_karet': 'BR049',
            'oven': 'Oven2'},
           {'spk_gips': 'SPK050',
            'pohon_id': 'TREE050',
            'Kadar': 'K050',
            'base_karet': 'BR050',
            'oven': 'Oven2'}];

        this.table_fields = [
            {fieldtype:'Link', fieldname:'spk_gips', label:'SPK Gips', options:'Work Order Gips', in_list_view:1, columns:2},
            {fieldtype:'Data', fieldname:'pohon_id', label:'Pohon ID', in_list_view:1, columns:2},
            {fieldtype:'Link', fieldname:'kadar', label:'Kadar', options:'Data Logam', in_list_view:1, columns:2},
            {fieldtype:'Data', fieldname:'base_karet', label:'Base Karet', in_list_view:1, columns:2},
            {fieldtype:'Select', fieldname:'oven', label:'Oven', options:'Oven1\nOven2\nOven3\nOven4\nOven5', in_list_view:1, columns:2}
        ];

        this.originalGridData = [
            ['A01-01-1-01', 'A01-01-2-01', 'A01-01-3-01', 'A01-01-4-01', 'A01-01-5-01'],
            ['A01-01-1-02', 'A01-01-2-02', 'A01-01-3-02', 'A01-01-4-02', 'A01-01-5-02'],
            ['A01-01-1-03', 'A01-01-2-03', 'A01-01-3-03', 'A01-01-4-03', 'A01-01-5-03'],
            ['A01-01-1-04', 'A01-01-2-04', 'A01-01-3-04', 'A01-01-4-04', 'A01-01-5-04'],
            ['A01-01-1-05', 'A01-01-2-05', 'A01-01-3-05', 'A01-01-4-05', 'A01-01-5-05']
        ];
        this.gridData = JSON.parse(JSON.stringify(this.originalGridData));

        this.make();
        this.setupDataTables(this.page.parent); 
    },

    setupFields: function() {
        var me = this;

        // Date Range field
        this.page.add_field({
            fieldtype: 'DateRange',
            fieldname: 'posting_date',
            label: __('Posting Date'),
            default: [frappe.datetime.add_days(frappe.datetime.now_date(), -30), frappe.datetime.now_date()],
            reqd: 1,
            change: function() {
                me.posting_date = this.get_value();
                me.make();
            }
        });

        // Used checkbox field
        this.page.add_field({
            fieldtype: 'Check',
            fieldname: 'used',
            label: __('Used'),
            default: 1,
            onchange: function() {
                me.used = this.get_value();
                me.make();
            }
        });

        // Instead of adding the Table field directly, we'll create a custom HTML field
        // this.page.add_field({
        //     fieldtype: 'Section Break',
        //     fieldname: 'section_break_html',
        // });
        // this.page.add_field({
        //     fieldtype: 'HTML',
        //     fieldname: 'details_html',
        //     label: __('Details'),
        //     options: '<div id="details-table">Hallo</div>'
        // });
    },

    make: function() {
        let me = this;
    
        let body = `<div style="margin-top:10px;"><h2>Peta Oven</h2><div class="grid" id="grid"></div><div class="buttons"><button id="saveBtn">Simpan</button><button id="resetBtn">Reset</button></div></div><div id="sidetable"><h2>Current Data State</h2><div id="dataTable"></div></div><div id="jsonOutput"></div>`;
        
        // Update only the content area
        this.content.html(body);

        this.page.main.css({
            'font-family': 'Arial, sans-serif'
        });

        frappe.dom.set_style(`
            .grid {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 10px;
            }
            .cell {
                position: relative;
                border: 1px solid #ccc;
                padding: 10px;
                text-align: center;
                background-color: #f0f0f0;
                cursor: move;
            }
            .cell .id {
                position: absolute;
                top: 5px;
                left: 5px;
                font-size: 0.8em;
                color: #555;
            }
            .cell .value {
                position: relative;
                font-size: 1.2em;
            }
            .cell.dragging {
                opacity: 0.5;
            }
            #sidetable {
                display:none;
            }
            table {
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            .buttons {
                margin-top: 20px;
            }
            button {
                margin-right: 10px;
                padding: 10px 20px;
            }
            .json-output {
                margin-top: 20px;
                border: 1px solid #ccc;
                padding: 10px;
                background-color: #f9f9f9;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
        `);

        this.createGrid();

        this.content.find('#saveBtn').on('click', () => {
            const jsonData = me.gridData.flatMap((row, rowIndex) => 
                row.map((item, colIndex) => ({
                    id: me.content.find(`[data-row="${rowIndex}"][data-col="${colIndex}"]`).attr('data-id'),
                    row: rowIndex + 1,
                    column: colIndex + 1,
                    value: item
                }))
            );
            const formattedJsonData = JSON.stringify(jsonData, null, 2);
            me.content.find('#jsonOutput').text(formattedJsonData);
        });

        this.content.find('#resetBtn').on('click', () => {
            me.gridData = JSON.parse(JSON.stringify(me.originalGridData));
            me.createGrid();
            me.content.find('#jsonOutput').text('');
        });
    },

    createGrid: function() {
        let me = this;
        let idCounter = 1;
        let grid = this.content.find('#grid');
        grid.empty();
        me.gridData.forEach((row, rowIndex) => {
            row.forEach((item, colIndex) => {
                const cell = $('<div>')
                    .addClass('cell')
                    .attr({
                        'draggable': true,
                        'data-row': rowIndex,
                        'data-col': colIndex,
                        'data-id': idCounter++
                    });

                $('<div>')
                    .addClass('id')
                    .text(cell.attr('data-id'))
                    .appendTo(cell);

                $('<div>')
                    .addClass('value')
                    .text(item)
                    .appendTo(cell);

                cell.on('dragstart', me.dragStart.bind(me))
                    .on('dragover', me.dragOver.bind(me))
                    .on('dragenter', me.dragEnter.bind(me))
                    .on('dragleave', me.dragLeave.bind(me))
                    .on('drop', me.drop.bind(me))
                    .on('dragend', me.dragEnd.bind(me));

                grid.append(cell);
            });
        });
    },

    dragStart: function(e) {
        this.draggedItem = e.target;
        setTimeout(() => e.target.classList.add('dragging'), 0);
    },

    dragOver: function(e) {
        e.preventDefault();
    },

    dragEnter: function(e) {
        e.preventDefault();
        e.target.classList.add('hovered');
    },

    dragLeave: function(e) {
        e.target.classList.remove('hovered');
    },

    drop: function(e) {
        e.preventDefault();
        const target = e.target.closest('.cell');
        if (!target || target === this.draggedItem) return;

        target.classList.remove('hovered');
        const fromRow = parseInt(this.draggedItem.getAttribute('data-row'));
        const fromCol = parseInt(this.draggedItem.getAttribute('data-col'));
        const toRow = parseInt(target.getAttribute('data-row'));
        const toCol = parseInt(target.getAttribute('data-col'));
        
        if (!isNaN(fromRow) && !isNaN(fromCol) && !isNaN(toRow) && !isNaN(toCol)) {
            const temp = this.gridData[fromRow][fromCol];
            this.gridData[fromRow][fromCol] = this.gridData[toRow][toCol];
            this.gridData[toRow][toCol] = temp;

            this.createGrid();
        }
    },

    dragEnd: function(e) {
        e.target.classList.remove('dragging');
    },

    setupDataTables: async function(wrapper) {
        let me = this;
    
            // Pastikan elemen '#datatable-container' ada
        let $datatable_container = this.page.main.find('#datatable-container');
        if ($datatable_container.length === 0) {
            // Jika tidak ada, tambahkan elemen kontainer ke halaman
            $datatable_container = $('<div id="datatable-container"></div>').appendTo(this.page.main);
        }

        // Memastikan elemen kontainer diambil dengan benar
        let wrapper_element = $datatable_container.get(0);
        if (!wrapper_element) {
            console.error("Element wrapper untuk DataTable tidak ditemukan.");
            return;
        }

        // Buat DataTable hanya jika wrapper valid
        let datatable = await new frappe.DataTable(wrapper_element, {
            columns: this.table_fields,
            data: this.data,
            layout: "fluid",
            serialNoColumn: false,
            checkboxColumn: true,
            cellHeight: 35,
        });
        
    },

    piutang: function() {
        var me = this;
        var data = frappe.call({
            method: 'lestari.lestari.page.kartu_piutang_custom.kartu_piutang_custom.contoh_report',
            args: {
                'posting_date': me.posting_date,
                'used': me.used
            }
        });
        return data;
    }
});