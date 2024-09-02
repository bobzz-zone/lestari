{% include 'lestari/public/js/custom/custom_multi_select.js' %}

frappe.ui.form.on('Purchase Invoice', {
	before_submit(frm){
	    // set_row_numbers(frm);
        if(frm.doc.data_is_in_erp == 1){
            return
        }else{
            $.each(frm.doc.items,function(i,g){
                if(!g.purchase_receipt){
                    frappe.throw("Purchase Invoice harus memiliki Purchase Receipt / BTB!!!")
                }
            })
        }
	},
})