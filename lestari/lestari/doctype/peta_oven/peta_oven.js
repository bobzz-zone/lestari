// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt
frappe.ui.form.on('Peta Oven', {
    // onload: function(frm) {
    //     // Mencegah modal child table untuk terbuka
    //     frm.fields_dict['list_spk'].grid.wrapper.on('click', '.grid-row', function(event) {
    //         // Cek apakah checkbox dicentang
    //         var checkbox = $(this).find('.grid-row-check');
    //         if (!checkbox.is(':checked')) {
    //             event.preventDefault(); // Mencegah aksi default
    //             event.stopPropagation(); // Mencegah event bubbling
    //         }
    //     });
    // },
    refresh: function(frm) {
  
        const total_pohon_div = `
			<div class="pohonDipilih" style="padding:0px 5px;background:#913030;font-weight:bold;margin:0px 13px 0px 2px;
				color:#f9fafa;font-size:18px;display:inline-block;vertical-align:text-bottom;>
				<span class="label_total">Total Pohon</span>
				<span class="colon">:</span>
				<span class="pohon_unused">0</span>
			</div>`;
	
		cur_frm.toolbar.page.add_inner_message(total_pohon_div);

        frm.fields_dict['list_spk'].grid.wrapper.on('change', '.grid-row-check', function(event) {
            var grid = frm.fields_dict['list_spk'].grid.grid_rows;
            let total_pohonan = 0;

            grid.forEach(function(row) {
                if (row && row.wrapper.find('.grid-row-check').is(':checked')) {
                    total_pohonan += row.doc.total_pohonan_unused; // Ganti dengan nama field yang sesuai
                }
            });

            // Tampilkan pesan dengan total_pohonan
            // frappe.msgprint(__('Total Pohonan: {0}', [total_pohonan]));
            $(".pohon_unused").text(total_pohonan);
        });

        if(frm.doc.list_spk){
            let total_pohonan = 0;
            $.each(frm.doc.list_spk, function(i, d) {
                total_pohonan += d.total_pohonan_unused;
            })
            $(".pohon_unused").text(total_pohonan);
        }

        // frm.fields_dict['list_spk'].grid.wrapper.css('pointer-events', 'none');

        if(frm.is_new()){
            frm.call({
                method: "get_spk_gips",
                doc: frm.doc,
                freeze: true,
                freeze_message: __("<h2><b>Get SPK Gips List...</b></h2>"),
                callback: function(response) {
                    frm.fields_dict['list_spk'].grid.wrapper.find('.btn-open-row').hide();
                    frm.set_df_property("list_spk", "in_place_edit", false);
                    frm.refresh_field('list_spk');
                }
            })
        }

        setupDragAndDropGrid(frm);

        setupCustomButtons(frm);

        frm.fields_dict['list_details_spk'].grid.wrapper.find('.btn-open-row').hide();
        frm.fields_dict['details'].grid.wrapper.find('.btn-open-row').hide();
    },

    after_save: function(frm) {
        setupDragAndDropGrid(frm);
    },

    get_spk_gips: function(frm) {
        frm.call("get_spk_gips").then(() => {
            frm.refresh_field("list_spk");
        });
    },
});

frappe.ui.form.on('Peta Oven SPK Gips', {
    idx: function(frm, cdt, cdn){
        console.log('testidx')
        return false;
    }
})

function setupDragAndDropGrid(frm) {
    let gridContainer = frm.fields_dict.peta_oven_grid && frm.fields_dict.peta_oven_grid.$wrapper;
    if (!gridContainer) {
        console.warn("Peta Oven grid container not found. Make sure you have an HTML field named 'peta_oven_grid'.");
        return;
    }

    let grid = gridContainer.find('#peta-oven-grid');
    if (grid.length === 0) {
        gridContainer.append('<div id="peta-oven-grid" class="grid"></div>');
        grid = gridContainer.find('#peta-oven-grid');
    }

    // Mengambil data dan tipe pohon dari dokumen
    const { gridData, treeType } = getGridDataAndType(frm);

    // Set up grid layout berdasarkan tipe pohon
    setGridLayout(grid, treeType);

    let draggedItem = null;

    function createGrid() {
        grid.empty(); // Clear existing grid
        gridData.forEach((item, index) => {
            const cell = $('<div>')
                .addClass('cell')
                .text(item)
                .attr('draggable', true)
                .attr('data-index', index);

            cell.on('dragstart', dragStart);
            cell.on('dragover', dragOver);
            cell.on('dragenter', dragEnter);
            cell.on('dragleave', dragLeave);
            cell.on('drop', drop);
            cell.on('dragend', dragEnd);

            grid.append(cell);
        });
    }

    function dragStart(e) {
        draggedItem = this;
        setTimeout(() => $(this).addClass('dragging'), 0);
    }

    function dragOver(e) {
        e.preventDefault();
    }

    function dragEnter(e) {
        e.preventDefault();
        $(this).addClass('hovered');
    }

    function dragLeave() {
        $(this).removeClass('hovered');
    }

    function drop() {
        $(this).removeClass('hovered');
        if (this !== draggedItem) {
            const fromIndex = parseInt($(draggedItem).attr('data-index'));
            const toIndex = parseInt($(this).attr('data-index'));
            
            const itemOne = gridData[fromIndex];
            const itemTwo = gridData[toIndex];
            
            gridData[fromIndex] = itemTwo;
            gridData[toIndex] = itemOne;
            
            $(this).attr('data-index', fromIndex);
            $(draggedItem).attr('data-index', toIndex);
            
            if (toIndex > fromIndex) {
                $(this).after(draggedItem);
            } else {
                $(this).before(draggedItem);
            }

            updateFormWithNewOrder(frm, gridData);
        }
    }

    function dragEnd() {
        $(this).removeClass('dragging');
    }

    function updateFormWithNewOrder(frm, newOrder) {
        // Update the details child table with the new order
        frm.doc.details.forEach((row, index) => {
            row.idx = index + 1;
            row.nomor_base_karet = newOrder[index];
        });
        frm.refresh_field('details');
    }

    createGrid();
}

function getGridDataAndType(frm) {
    if (!frm.doc.details || !frm.doc.details.length) {
        console.warn("No details found in the document.");
        return { gridData: [], treeType: 'Emas' }; // Default to Emas if no data
    }
    const treeType = frm.doc.type_pohonan || 'Emas'; // Assume there's a field called 'type_pohonan'
    return {
        gridData: frm.doc.details.map(row => row.nomor_base_karet),
        treeType: treeType
    };
}

function setGridLayout(grid, treeType) {
    let columns, rows;
    switch (treeType) {
        case 'Emas':
            columns = 5;
            rows = 5;
            break;
        case 'Perak':
            columns = 6;
            rows = 1;
            break;
        case 'Direct Casting':
            columns = 6;
            rows = 2;
            break;
        default:
            columns = 5;
            rows = 5; // Default to Emas layout
    }

    grid.css({
        'grid-template-columns': `repeat(${columns}, 1fr)`,
        'grid-template-rows': `repeat(${rows}, 1fr)`
    });

    // Adjust cell size based on the number of columns
    const cellWidth = 100 / columns;
    grid.find('.cell').css('width', `${cellWidth}%`);
}

function setupCustomButtons(frm) {
    if (frm.fields_dict.list_spk && frm.fields_dict.list_spk.grid) {
        frm.add_custom_button(__('Pilih Permintaan'), function() {
            delete_unselected_rows(frm);
        });

        frm.add_custom_button(__('Buat Peta Oven'), function() {
            // frm.call("get_spk_gips_details").then((r) => {
            //     console.log(r)
            //     frm.refresh_field("list_spk");
            // });
            fetchGipsDetails(frm);
        });
    }
}

function delete_unselected_rows(frm) {
    let grid = frm.fields_dict.list_spk.grid;
    
    let selected_indices = new Set(grid.get_selected_children().map(d => d.idx - 1));
    console.log("Baris terpilih:", selected_indices.size);

    let all_items = frm.doc.list_spk || [];
    console.log("Semua item:", all_items.length);
    
    let unselected_items = all_items.filter((_, index) => !selected_indices.has(index));
    console.log("Item tidak terpilih:", unselected_items.length);
    
    if (!unselected_items.length) {
        frappe.msgprint(__("Tidak ada baris yang tidak terpilih untuk dihapus."));
        return;
    }

    frappe.confirm(__("Anda yakin ingin menghapus {0} baris yang tidak terpilih?", [unselected_items.length]),
        () => {
            frappe.show_progress('Menghapus baris...', 0, 100);
            
            const batchSize = 50;
            const totalBatches = Math.ceil(unselected_items.length / batchSize);
            
            const deleteBatch = (batchIndex) => {
                if (batchIndex >= totalBatches) {
                    frappe.hide_progress();
                    
                    // Mengurutkan ulang indeks item
                    frm.doc.list_spk.forEach((item, index) => {
                        item.idx = index + 1;
                        item.pr_ordinal = index + 1;
                    });
                    
                    frm.refresh_field('list_spk');
                    
                    // Menghilangkan semua centang setelah penghapusan selesai
                    frm.doc.list_spk.forEach((item, index) => {
                        item.__checked = 0;                        
                    });
                    
					frm.refresh_field('list_spk');

                    frappe.show_alert(__("{0} baris dihapus. Semua centang telah dihapus dan nomor baris telah diurutkan ulang.", [unselected_items.length]));
					setTimeout(function(){
						fetchGipsDetails(frm);
					}, 1500);
                    return;
                }

                const start = batchIndex * batchSize;
                const end = Math.min(start + batchSize, unselected_items.length);
                const itemsToDelete = unselected_items.slice(start, end);

                const itemNamesToDelete = new Set(itemsToDelete.map(item => item.name));
                frm.doc.list_spk = frm.doc.list_spk.filter(item => !itemNamesToDelete.has(item.name));

                frappe.show_progress('Menghapus baris...', (batchIndex + 1) * 100 / totalBatches, 100);
                
                setTimeout(() => deleteBatch(batchIndex + 1), 0);
            };

            deleteBatch(0);		
        }
    );
}

function fetchGipsDetails(frm) {
    frm.call({
        method: "get_spk_gips_details",
        doc: frm.doc,
        callback: function(response) {
            if (response.message) {
                const sortedRows = response.message; // Get the sorted rows

                // Assuming 'details' is the child table fieldname in the parent doctype
                const childTable = cur_frm.doc.details; // Access the child table data

                // Clear existing child table entries
                cur_frm.clear_table("details");

                // Loop through sorted rows and append to child table
                sortedRows.forEach(function(row) {
                    if(frm.doc.type_pohonan == 'Emas' && row.kadar){
                        const newRow = cur_frm.add_child("details"); // Add a new row
                        Object.assign(newRow, row); // Copy data to the new row
                    }
                });

                // Refresh the child table to show the new rows
                cur_frm.refresh_field("details");
            }
        }
    });
}

// Fungsi untuk menghitung total pohonan
function calculateTotalPohonan(frm) {
    let total_pohonan = 0;

    // Loop melalui child table untuk menghitung total_pohonan
    frm.doc.list_spk.forEach((row) => {
        if(row.checked) {  // Pastikan untuk memeriksa apakah checkbox dicentang
            total_pohonan += row.total_pohonan_unused;  // Ganti dengan nama field yang sesuai
        }
    });

    // Tampilkan pesan dengan total_pohonan
    frappe.msgprint(__('Total Pohonan: {0}', [total_pohonan]));
}