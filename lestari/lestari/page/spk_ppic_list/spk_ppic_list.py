# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import *

@frappe.whitelist()
def contoh_report():
    fm = []
    list_doc = frappe.get_list("Form Order", limit=1000)
    no = 0
    for row in list_doc:
        doc = frappe.get_doc("Form Order", row)
        for col in doc.items_valid:
            no+=1
            baris_baris = {
                'no' : no,
                    'name' : str(doc.idworksuggestion),
                    'urut_fm' : str(col.idx),
                    'model' : col.model,
                    'qty' : col.qty,
                    'berat' : 0,
                    'posting_date' : frappe.format(doc.posting_date,{'fieldtype':'Date'}),
                    # 'posting_date' : frappe.date.datetime(doc.posting_date,"M/d/yyyy"),
                    'kadar' : doc.kadar,
                    'kategori' : doc.kategori,
                    'sub_kategori' : doc.sub_kategori,
            }
            fm.append(baris_baris)
    # frappe.msgprint(str(fm))  
    return fm   