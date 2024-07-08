# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import *
import json

@frappe.whitelist()
def make_po(data,supplier = None, combine = None, pajak = None, ppn = None, tujuan = None, no_faktur = None, submitted = None):
    # frappe.throw(str(json.loads(data)))
    list_name = tuple(json.loads(data))
    if len(list_name) > 1:
        condition = """WHERE b.name IN {}""".format(str(list_name))
    else:
        doc_name = json.loads(data)
        result = str(doc_name[0])
        condition = """WHERE b.name = '{}'""".format(result)
    # frappe.msgprint(str(list_name))
    mr_list = frappe.db.sql("""
        SELECT 
        a.transaction_date, a.name, a.schedule_date, 
        b.name as IDM, b.item_code, b.schedule_date, b.item_name, b.description, b.keterangan, b.qty, b.uom, b.stock_uom, b.conversion_factor
        FROM `tabMaterial Request` a JOIN `tabMaterial Request Item` b ON a.name = b.parent {}
    """.format(condition),as_dict=1)
    # frappe.msgprint(str(mr_list))
    new_doc = frappe.new_doc("Purchase Order")
    new_doc.naming_series = "PO.YY.MM.DD.###"
    new_doc.transaction_date = mr_list[0].transaction_date
    required_date = mr_list[0].schedule_date
    new_doc.tujuan = tujuan
    new_doc.pajak = pajak
    new_doc.ppn = ppn
    new_doc.no_faktur = no_faktur
    new_doc.supplier = supplier
    for row in mr_list:
        baris_baru = {
            "item_code": row['item_code'],
            "schedule_date": required_date,
            "item_name": row['item_name'],
            "description": row['description'],
            "keterangan": row['keterangan'],
            "qty": row['qty'],
            "uom": row['uom'],
            "stock_uom": row['stock_uom'],
            "conversion_factor": row['conversion_factor']
        }
        new_doc.append("items",baris_baru)
    new_doc.flags.ignore_permissions = True
    new_doc.save()
    if submitted and submitted == 1:
        new_doc.submit()
    frappe.msgprint("PO Berhasil dibuat dengan Nomor"+str(new_doc))
    return new_doc.as_dict()

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None, args=None):
	doclist = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Purchase Order",
				"validation": {"docstatus": ["=", 1], "material_request_type": ["=", "Purchase"]},
			},
			"Material Request Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "material_request_item"],
					["parent", "material_request"],
					["uom", "stock_uom"],
					["uom", "uom"],
				],
			},
		},
	)

	return doclist

@frappe.whitelist()
def contoh_report():
    po = []
    # list_doc = frappe.get_list("Form Order", filters={'docstatus':1},order_by="posting_date DESC",limit = 5000)
    list_doc = frappe.db.sql("""
        SELECT a.name as ID, a.idmaterial_request, a.department, a.employee_name, a.status, a.transaction_date, a.schedule_date,b.name as IDM, b.ordered_qty, b.item_code, b.`description`, b.qty
        FROM `tabMaterial Request` a
        JOIN `tabMaterial Request Item` b 
        ON a.name = b.parent
        WHERE a.docstatus = 1 AND a.status = "Pending" AND a.material_request_type IN ('Purchase','Partially Ordered')
        
    """,as_dict = 1)
    # frappe.msgprint(str(list_doc))
    no = 0
    for row in list_doc:
        no+=1
        baris_baris = {
            'no' : no,
                'no_mr' : row.ID,
                'idm' : row.IDM,
                'idmaterial_request': row.idmaterial_request,
                'status' : row.status,
                'employee_name' : row.employee_name,
                'department' : row.department,
                'transaction_date' : frappe.format(row.transaction_date,{'fieldtype':'Date'}),
                'schedule_date' : frappe.format(row.schedule_date,{'fieldtype':'Date'}),
                'item_code' : row.item_code,
                'description' : row.description,
                'qty' : row.qty,
                'ordered_qty' : row.ordered_qty
        }
        po.append(baris_baris)
    # frappe.msgprint(str(po))  
    return po   