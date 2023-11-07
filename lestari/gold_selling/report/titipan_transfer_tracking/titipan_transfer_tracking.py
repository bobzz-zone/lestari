# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe


#buatin report cross check "Titipan Transfer Tracking"
#js e cm date, from_date sama to_date

#TOT di buat di sini juga
def execute(filters=None):
	columns, data = ["Date:date:80","No Nota TOT:Data:100","Type Nota:Data:100","Dari Customer:Link/Customer:100","Status:Data:50","Berat 24K Titipan:Float:80","Tutupan:Currency:100","Nilai Titipan:Currency:100","Supplier:Link/Supplier:80","No Invoice Pembelian:Link/Purchase Invoice:100"], []

	#date di filter untuk mendapatkan tanggal transaksi oper transfernya
	#dapatkan data Gold Payment Titipan di union dengan data Customer Deposit Titipan
	data=frappe.db.sql("""
		select if(sp.parenttype="Customer Deposit",cd.posting_date,gp.posting_date) as "date",sp.parent,sp.parenttype,if(sp.parenttype="Customer Deposit",cd.customer,gp.customer) as "dari_customer",if(sp.reference_name="","Pending","Done"),sp.amount,if(sp.parenttype="Customer Deposit",cd.tutupan,gp.tutupan) as "tutupan",sp.amount * if(sp.parenttype="Customer Deposit",cd.tutupan,gp.tutupan),sp.supplier,sp.reference_name from `tabStock Payment` sp 
		left join `tabGold Payment` gp on sp.parent = gp.name and sp.parenttype="Gold Payment"
		left join `tabCustomer Deposit` cd on sp.parent = cd.name and sp.parenttype="Customer Deposit"
		where sp.docstatus=1 and sp.in_supplier=1 and sp.amount>0 and ((cd.posting_date<="{0}" and cd.posting_date>="{1}") or (cd.posting_date<="{0}" and cd.posting_date>="{1}")) order by date
		 """.format(filters.get("to_date"),filters.get("from_date")),as_list=1)

	return columns, data