# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, data = [], []
	columns= ["Posting Date:Date:150","Voucher Type:Data:100","Voucher No:Data:100","Item:Data:125","Qty:Float:100","Rate:Float:100","24K:Float:150","Balance:Float:150"]
	#saldo awal
	saldo_awal=frappe.db.sql("""select sum(netto) as total from `tabGold Log` where customer="{}" and date < "{}" group by customer """.format(filters.get("customer"),filters.get("from_date")),as_list=1)
	saldo=0
	if saldo_awal:
		saldo=flt(saldo_awal[0][0])
		data.append(["","","","Saldo Awal","","","",saldo])
	#mutasi
	log_data = frappe.db.sql("""select date, voucher_type,voucher_no , item,bruto,rate,netto from `tabGold Log` 
		where customer="{}" and date <= "{}" and date >="{}" order by date asc
	 """.format(filters.get("customer"),filters.get("to_date"),filters.get("from_date")))
	for row in log_data:
		saldo=saldo+flt(row[6])
		data.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],saldo])
	return columns, data
