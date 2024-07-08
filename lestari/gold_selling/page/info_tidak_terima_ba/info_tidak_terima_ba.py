# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import now,today,add_days,flt
from datetime import datetime
import json

@frappe.whitelist()
def contoh_report(posting_date = None, used = None):
    if posting_date:
        json_data = json.loads(posting_date)
    else:
        input_dt = datetime.today()
        res = input_dt.replace(day=1)
        json_data = ['2023-10-31', today()]
    # frappe.msgprint(str(res.date()))
    piutang = []
    condition = ""
    if used == 1:
        condition = """AND a.gold_left <= 0"""

    list_doc = frappe.db.sql("""
            SELECT
            a.posting_date,
            a.name,
            "Customer Deposit" as voucher_type,
            a.no_nota,
            a.customer,
            a.type_emas,
            a.tutupan,
            a.sales_bundle,
            a.total_gold_deposit,
            a.gold_left,
            b.idx,
            b.item,
            b.qty,
            b.rate,
            b.amount,
            b.keterangan,
            b.`supplier`
            FROM
            `tabCustomer Deposit` a
            JOIN `tabStock Payment` b
            ON b.parent = a.name
            WHERE b.`in_supplier` = 1
            {}
    """.format(condition),as_dict = 1)
    # no = 0
    url = "http://erpnext.lestarigold.co.id/app"
    for row in list_doc:
        doctype = row.voucher_type.lower().replace(' ', '-')
        # no+=1
        baris_baris = {
            # 'no' : no,
            'customer' : row.customer,
            'no_nota' : row.no_nota,
            # 'voucher_type' : row.voucher_type,
            # 'bundle' : row.sales_bundle,
            'urut' : row.idx,
            'tgl_bayar' : "",
            'berat' : flt(row.qty,3),
            'nilai_tukar' : flt(row.tutupan,2),
            'nilai' : flt(row.tutupan * row.qty,2),
            'voucher_no' : row.name,
            'tanggal' : row.posting_date,
            'supplier' : row.supplier,
            # 'jenis_emas' : row.type_emas,
            'item' : row.item,
            'keterangan' : row.keterangan
        }
        piutang.append(baris_baris)
    # frappe.msgprint(str(piutang))  
    return piutang   