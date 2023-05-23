# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, data = ["Date:Date:150","Type:Data:150","Voucher No:Data:150","Sales:Data:150","Outstanding:Float:150","Balance Gold:Float:150","Total Titipan Rupiah:Currency:150"], []
	
	mutasi=frappe.db.sql("""select x.posting_date,x.type,x.voucher_no, sb.sales,x.outstanding,x.titipan from 
		(select gi.posting_date as "date","Gold Invoice as "type" ,gi.name as "voucher_no" , gi.sales_bundle, outstanding , 0 as "titipan"
		from `tabGold Invoice` gi where docstatus=1 and outstanding>0 
		UNION 
		select cd.posting_date,"Customer Deposit" as "type" , cd.name as "voucher_no" ,cd.sales_bundle, (gold_left*-1) as outstanding , (idr_left*-1) as "titipan"
		from `tabCustomer Deposit` cd where docstatus=1 and (idr_left >0  or gold_left >0)
		) x left join `tabSales Stock Bundle` sb on x.sales_bundle = sb.name
		order by x.posting_date asc
		""", as_list=1)
	balance=0
	for row in mutasi:
		balance=balance+flt(row[4])
		data.append(row[0],row[1],row[2],row[3],row[4],balance,row[5])
	return columns, data
