from __future__ import unicode_literals
import frappe
from frappe.utils import now,today,add_days,flt
from datetime import datetime
import json

@frappe.whitelist()
def contoh_report(posting_date = None):
    janji_bayar = []
    if posting_date:
        json_data = json.loads(posting_date)
    else:
        input_dt = datetime.today()
        res = input_dt.replace(day=1)
        json_data = [res.date(), today()]
    list_doc = frappe.db.sql("""
	select customer,name ,jenis_janji, tanggal_janji,total_terbayar,total_bayar,sisa_janji,status from `tabJanji Bayar` 
	where docstatus=1 and (tanggal_janji BETWEEN "{0}" AND "{1}")
    """.format(json_data[0],json_data[1]),as_dict = 1)
    no = 0
    for row in list_doc:
        no+=1
        baris_baris = {
            'no' : no,
            'janji_bayar' : row.name,
            'customer' : row.customer,
            'tanggal_janji' : row.tanggal_janji,
            'jenis_janji' : row.jenis_janji,
            'status' : row.status,
            'total_janji_bayar' : row.total_bayar,
            'total_terbayar' : row.total_terbayar,
            'sisa_janji' : row.sisa_janji,
            'detail' : frappe.db.sql("""SELECT
                                            pjb.janji_bayar,
                                            pjb.parent AS "no_voucher",
                                            pjb.parenttype AS "voucher_type",
                                            IF(
                                                pjb.parenttype = "Customer Deposit",
                                                cd.posting_date,
                                                gp.posting_date
                                            ) AS "date",
                                            pjb.allocated_janji
                                            FROM
                                            `tabPembayaran Janji Bayar` pjb
                                            LEFT JOIN `tabGold Payment` gp
                                                ON pjb.parent = gp.name
                                                AND pjb.parenttype = "Gold Payment"
                                            LEFT JOIN `tabCustomer Deposit` cd
                                                ON pjb.parent = cd.name
                                                AND pjb.parenttype = "Customer Deposit"
                                            WHERE pjb.docstatus = 1
                                            AND pjb.allocated_janji > 0
                                            AND (
                                                pjb.tanggal_janji BETWEEN "{}"
                                                AND "{}"
                                            )
                                            ORDER BY janji_bayar,
                                            DATE
            """.format(),as_dict=1),
            # 'detail' : frappe.db.get_list("Pembayaran Janji Bayar", filters={'janji_bayar':row.name,'parenttype':row.parenttype},fields=['janji_bayar','parent','parenttype','allocated_janji']),
            # 'customer_deposit' : frappe.db.get_list("Pembayaran Janji Bayar", filters={'janji_bayar':row.name,'parenttype':'Customer Deposit'},fields=['janji_bayar','parent','parenttype','allocated_janji'])
        }
        janji_bayar.append(baris_baris)
        # frappe.msgprint(str(baris_baris))
    return janji_bayar   