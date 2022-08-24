# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ProsesPohonanLilin(Document):
    def validate(doc):
        pass
        # if(doc.status == "Cor"):
        #     frappe.msgprint('COR')
        #     data_pohon = frappe.get_doc("Data Pohon Lilin", doc.pohon_lilin)
        #     data_pohon.berat_emas = "1000"
        #     data_pohon.uom_emas = "Gram"
        #     data_pohon.flags.ignore_permissions = True
        #     data_pohon.save()

@frappe.whitelist()
def make_stock_entry(no_dpl,no_ppl,status):
    # frappe.msgprint(status)
    target_doc = frappe.new_doc("Stock Entry")
    target_doc.stock_entry_type = "Material Transfer"
    # frappe.msgprint(no_dpl)
    
    sumber_doc = frappe.get_doc("Proses Pohonan Lilin", no_ppl)

    if( status == "Supermarket" ):
        sumber_sprue = frappe.db.sql("""
        SELECT
        ppl.main_sprue,
        item.item_code,
        item.stock_uom AS uom,
        itemdef.default_warehouse AS s_warehouse
        FROM `tabProses Pohonan Lilin` ppl
        JOIN `tabData Pohon Lilin` dpl ON dpl.main_sprue = ppl.main_sprue
        JOIN `tabData Main Sprue` dms ON dms.name = dpl.main_sprue
        JOIN `tabItem` item ON item.item_code = dms.name
        JOIN `tabItem Default` itemdef ON itemdef.parent = item.item_code
        WHERE ppl.name = "{}" AND dpl.name = "{}"
        """.format(no_ppl, no_dpl), as_dict=1)

        for row in sumber_sprue:
            baris_baru = {
                    "item_code": row.item_code,
                    "qty": 1,
                    "uom" : row.uom,
                    "conversion_factor" : 1,
                    "t_warehouse" : "Work In Progress - L",
                    "s_warehouse" : row.s_warehouse
                    }
            target_doc.append("items",baris_baru)

        sumber_material = frappe.db.sql("""
        SELECT DISTINCT
        pplm.name1 AS item_code,
        pplm.qty AS qty,
        pplm.uom AS uom,
        dplr.resep_cetakan AS resep,
        itemdef.default_warehouse AS s_warehouse
        FROM `tabProses Pohonan Lilin` ppl
        JOIN `tabData Pohon Lilin Resep` dplr ON dplr.parent = "{}"
        JOIN `tabResep Investment Lilin Batu` rilb ON rilb.parent = dplr.resep_cetakan
        JOIN `tabProses Pohonan Lilin Material` pplm ON pplm.name1 = rilb.batu
        JOIN `tabItem Default` itemdef ON itemdef.parent = pplm.name1
        WHERE pplm.parent = "{}" ORDER BY pplm.name1
        """.format(no_dpl,no_ppl), as_dict=1)

        for row in sumber_material:

            serialqty = frappe.db.sql("""
            SELECT 
            qty
            FROM `tabData Pohon Lilin Resep`
            WHERE parent = "{}" and resep_cetakan = "{}"
            GROUP BY resep_cetakan
            """.format(no_dpl, row.resep), as_dict=1)

            baris_baru = {
                    "item_code": row.item_code,
                    "qty": row.qty * serialqty[0].qty,
                    "uom" : row.uom,
                    "conversion_factor" : 1,
                    "t_warehouse" : "Work In Progress - L",
                    "s_warehouse" : row.s_warehouse
                    }
            target_doc.append("items",baris_baru)
            # frappe.msgprint(str(baris_baru))

        sumber_query = frappe.db.sql("""
        SELECT 
        ppls.rubber_mould,
        ppls.source_warehouse,
        ppls.uom,
        ppls.resep,
        COUNT(ppls.serial) AS qty,
        GROUP_CONCAT(DISTINCT ppls.serial) AS serial
        FROM `tabProses Pohonan Lilin Serial` ppls
        WHERE parent = "{}"
        GROUP BY ppls.rubber_mould
        ORDER BY GROUP_CONCAT(DISTINCT ppls.serial) ASC
        """.format(no_ppl), as_dict=1)

        for row in sumber_query:
            rserial = row.serial
            # frappe.msgprint(str(rserial))
            serial = rserial.replace(",","\n")

            baris_baru = {
                    "item_code": row.rubber_mould,
                    "qty": row.qty,
                    "uom" : row.uom,
                    "conversion_factor" : 1,
                    "t_warehouse" : "Work In Progress - L",
                    "s_warehouse" : row.source_warehouse,
                    "serial_no" : serial
                    }
            target_doc.append("items",baris_baru)

    if( status == "Gypsum" ):
        sumber_gypsum = frappe.db.sql("""
        SELECT 
        ppl.main_sprue, 
        dms.gips,
        dms.qty,
        dms.uom,
        itemdef.default_warehouse AS s_warehouse 
        FROM `tabProses Pohonan Lilin` ppl 
        JOIN `tabData Pohon Lilin` dpl ON dpl.main_sprue = ppl.main_sprue 
        JOIN `tabData Main Sprue` dms ON dms.name = dpl.main_sprue 
        JOIN `tabItem Default` itemdef ON itemdef.parent = dms.gips 
        WHERE ppl.name = "{}" AND dpl.name = "{}"
        LIMIT 1
        """.format(no_ppl, no_dpl),as_dict=1)

        for row in sumber_gypsum:
            baris_baru = {
                    "item_code": row.gips,
                    "qty": row.qty,
                    "uom" : row.uom,
                    "conversion_factor" : 1,
                    "t_warehouse" : "Work In Progress - L",
                    "s_warehouse" : row.s_warehouse
                    }
            frappe.msgprint(baris_baru)
            target_doc.append("items",baris_baru)

    if( status == "Cor" ):
        frappe.msgprint(no_ppl+","+no_dpl+","+status)
        sumber_emas = frappe.db.sql("""
        SELECT
        dpl.berat_gypsum,
        item.item_code,
        item.stock_uom,
        itemdef.default_warehouse
        FROM `tabProses Pohonan Lilin` ppl 
        JOIN `tabData Pohon Lilin` dpl ON dpl.name = ppl.pohon_lilin 
        JOIN `tabItem` item ON item.item_code = dpl.logam 
        JOIN `tabItem Default` itemdef ON itemdef.parent = item.item_code
        WHERE ppl.name = "{}" AND dpl.name = "{}"
        LIMIT 1
        """.format(no_ppl, no_dpl),as_dict=1)
        qty = 0
        uom = ""

        for row in sumber_emas:

            qty = row.berat_gypsum * 2
            uom = row.stock_uom

            baris_baru = {
                    "item_code": row.item_code,
                    "qty": qty,
                    "uom" : uom,
                    "conversion_factor" : 1,
                    "t_warehouse" : "Work In Progress - L",
                    "s_warehouse" : row.default_warehouse
                    }
            frappe.msgprint(baris_baru)
            target_doc.append("items",baris_baru)

        data_pohon = frappe.get_doc("Data Pohon Lilin", no_dpl)
        data_pohon.berat_emas = qty
        data_pohon.uom_emas = uom
        data_pohon.flags.ignore_permissions = True
        data_pohon.save()
    
    target_doc.ignore_permissions = True
    target_doc.save()
    return target_doc.as_dict()

@frappe.whitelist()
def get_serial(data_pohon):
	sumber_resep = frappe.db.sql("""
    SELECT 
    *
    FROM `tabData Pohon Lilin` dpl 
    JOIN `tabData Pohon Lilin Serial` dpls ON dpls.parent = dpl.name 
    WHERE dpl.name = "{}"
	ORDER BY dpls.serial
    """.format(data_pohon),as_dict=1)
	return sumber_resep

@frappe.whitelist()
def get_material(data_pohon):
    sumber_batu = frappe.db.sql("""
    SELECT 
    dplrsp.resep_cetakan,
    dplrsp.kode_perhiasan,
    dplrsp.rubber_mould,
    rilb.batu as nama_batu,
    rilb.uom,
    rilb.qty
    FROM `tabData Pohon Lilin` dpl 
    JOIN `tabData Pohon Lilin Resep` dplrsp ON dplrsp.parent = dpl.name 
    JOIN `tabResep Investment Lilin` ril ON ril.name = dplrsp.resep_cetakan
    JOIN `tabResep Investment Lilin Batu` rilb ON rilb.parent = ril.name
    WHERE dpl.name = "{}"
    """.format(data_pohon),as_dict=1)

    return sumber_batu

@frappe.whitelist()
def make_proses_pohonan_lilin(no_dpl,no_ppl,status):
    # frappe.msgprint(status)
    sumber_doc = frappe.get_doc("Data Pohon Lilin", no_dpl)

    target_doc = frappe.new_doc("Proses Pohonan Lilin")
    target_doc.title = no_ppl+"-"+status
    target_doc.insert()
    target_doc.proses_by = sumber_doc.created_by
    target_doc.proses_date = sumber_doc.created_date
    target_doc.proses_time = sumber_doc.created_time
    target_doc.pohon_lilin = no_dpl
    target_doc.main_sprue = sumber_doc.main_sprue

    sumber_rubber = frappe.db.sql("""
    SELECT 
    * 
    FROM `tabData Pohon Lilin` dpl 
    JOIN `tabData Pohon Lilin Serial` dpls ON dpls.parent = dpl.name 
    WHERE dpl.name = "{}" 
    ORDER BY dpls.serial DESC
    """.format(no_dpl),as_dict=1)

    for row in sumber_rubber:
        baris_baru = {
                "serial": row.serial,
                "resep": row.resep,
                "kode_perhiasan" : row.kode_perhiasan,
                "rubber_mould" : row.rubber_mould,
                "qty" : row.qty,
                "uom" : row.uom,
                "source_warehouse" : row.source_warehouse,
                "status" : row.status,
                "jumlah_pembelian" : row.jumlah_pembelian,
                }
        target_doc.append("rubber_mould",baris_baru)

    sumber_batu = frappe.db.sql("""
    SELECT 
    dplrsp.resep_cetakan,
    dplrsp.kode_perhiasan,
    dplrsp.rubber_mould,
    rilb.batu as nama_batu,
    rilb.uom,
    rilb.qty
    FROM `tabData Pohon Lilin` dpl 
    JOIN `tabData Pohon Lilin Resep` dplrsp ON dplrsp.parent = dpl.name 
    JOIN `tabResep Investment Lilin` ril ON ril.name = dplrsp.resep_cetakan
    JOIN `tabResep Investment Lilin Batu` rilb ON rilb.parent = ril.name
    WHERE dpl.name = "{}"
    """.format(no_dpl),as_dict=1)
    for row in sumber_batu:
        baris_baru = {
                "name1": row.nama_batu,
                "qty" : row.qty,
                "uom" : row.uom
                }
        target_doc.append("material",baris_baru)

    target_doc.status = status
    target_doc.flags.ignore_permissions = True
    target_doc.save()
    return target_doc.as_dict()