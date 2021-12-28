# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DataPohonLilin(Document):
    def validate(self):
        pass
    def on_update(self):
        pass

@frappe.whitelist()
def make_proses_pohonan_lilin(no_dpl):
    sumber_doc = frappe.get_doc("Data Pohon Lilin", no_dpl)

    target_doc = frappe.new_doc("Work Order Pohonan")
    target_doc.created_by = sumber_doc.created_by
    target_doc.created_date = sumber_doc.created_date
    target_doc.created_time = sumber_doc.created_time
    target_doc.status = "Plan"
    target_doc.pohon_id = no_dpl
    target_doc.warehouse_wip = "Work In Progress - L"

    sumber_batu = frappe.db.sql("""
    SELECT
    dplrsp.resep_cetakan, 
    rilb.batu as nama_batu,
    rilb.uom,
    rilb.qty
    FROM `tabData Pohon Lilin` dpl 
    JOIN `tabData Pohon Lilin Resep` dplrsp ON dplrsp.parent = dpl.name 
    JOIN `tabResep Mul Karet` ril ON ril.name = dplrsp.resep_cetakan
    JOIN `tabResep Investment Lilin Batu` rilb ON rilb.parent = ril.name
    WHERE dpl.name = "{}"
    """.format(no_dpl),as_dict=1)
    for row in sumber_batu:
        
        resepqty = frappe.db.sql("""
        SELECT 
        qty
        FROM `tabData Pohon Lilin Resep`
        WHERE parent = "{}" and resep_cetakan = "{}"
        """.format(no_dpl, row.resep_cetakan), as_dict=1)

        qty = resepqty[0].qty * row.qty
        
        baris_baru = {
                "material": row.nama_batu,
                "qty" : qty,
                "uom_qty" : row.uom,
                "berat" : 0,
                "uom_berat" : "Gram"
                }
        target_doc.append("material",baris_baru)
    # target_doc.flags.ignore_permissions = True
    # target_doc.save()
    return target_doc.as_dict()