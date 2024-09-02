# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def get_columns():
    return [
        {"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 150},
        {"fieldname": "voucher_type", "label": "Voucher Type", "fieldtype": "Data", "width": 100},
        {"fieldname": "voucher_no", "label": "Voucher No", "fieldtype": "Dynamic Link", "width": 100, "options":"voucher_type"},
        {"fieldname": "item", "label": "Item", "fieldtype": "Data", "width": 125},
        {"fieldname": "qty", "label": "Qty", "fieldtype": "Float", "width": 100},
        {"fieldname": "rate", "label": "Rate", "fieldtype": "Float", "width": 100},
        {"fieldname": "24k", "label": "24K", "fieldtype": "Float", "width": 150},
        {"fieldname": "balance", "label": "Balance", "fieldtype": "Float", "width": 150},
        {"fieldname": "blank", "label": " ", "fieldtype": "Data", "width": 10}
    ]

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_data(filters):
    data = []
    
    # Saldo awal
    saldo_awal = frappe.db.sql("""
        SELECT SUM(netto) AS total 
        FROM `tabGold Log` 
        WHERE customer = %(customer)s AND date < %(from_date)s 
        GROUP BY customer
    """, {"customer": filters.get("customer"), "from_date": filters.get("from_date")}, as_list=1)
    
    saldo = 0
    if saldo_awal:
        saldo = flt(saldo_awal[0][0])
        data.append({
            "posting_date": "",
            "voucher_type": "",
            "voucher_no": "",
            "item": "Saldo Awal",
            "qty": "",
            "rate": "",
            "24k": "",
            "balance": saldo,
            "blank": ""
        })
    
    # Mutasi
    log_data = frappe.db.sql("""
        SELECT date, voucher_type, voucher_no, item, bruto, rate, netto 
        FROM `tabGold Log` 
        WHERE customer = %(customer)s AND date <= %(to_date)s AND date >= %(from_date)s 
        ORDER BY date ASC, voucher_no
    """, {
        "customer": filters.get("customer"),
        "to_date": filters.get("to_date"),
        "from_date": filters.get("from_date")
    }, as_dict=1)
    
    for row in log_data:
        saldo += flt(row.netto)
        data.append({
            "posting_date": row.date,
            "voucher_type": row.voucher_type,
            "voucher_no": row.voucher_no,
            "item": row.item,
            "qty": row.bruto,
            "rate": row.rate,
            "24k": row.netto,
            "balance": saldo,
            "blank": ""
        })
    
    return data

	# def execute(filters=None):
	# columns, data = [], []
	# columns= ["Posting Date:Date:150","Voucher Type:Data:100","Voucher No:Data:100","Item:Data:125","Qty:Float:100","Rate:Float:100","24K:Float:150","Balance:Float:150"," _ :Data:10"]
	# #saldo awal
	# saldo_awal=frappe.db.sql("""select sum(netto) as total from `tabGold Log` where customer="{}" and date < "{}" group by customer """.format(filters.get("customer"),filters.get("from_date")),as_list=1)
	# saldo=0
	# if saldo_awal:
	# 	saldo=flt(saldo_awal[0][0])
	# 	data.append(["","","","Saldo Awal","","","",saldo,""])
	# #mutasi
	# log_data = frappe.db.sql("""select `date`, voucher_type,voucher_no , item,bruto,rate,netto from `tabGold Log` 
	# 	where customer="{}" and date <= "{}" and date >="{}" order by `date` asc , voucher_no
	#  """.format(filters.get("customer"),filters.get("to_date"),filters.get("from_date")))
	# for row in log_data:
	# 	saldo=saldo+flt(row[6])
	# 	data.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],saldo,""])
	# return columns, data
