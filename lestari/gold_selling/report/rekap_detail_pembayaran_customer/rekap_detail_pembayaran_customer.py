# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	data = frappe.db.sql("""select cd.posting_date,cd.no_nota,cd.name as "Document No",sp.item,sp.qty,sp.rate,sp.amount,sp.keterangan from `tabStock Payment` sp left join `tabCustomer Deposit` cd on sp.parent=cd.name
							where cd.docstatus=1 and cd.customer="{customer}" and (cd.posting_date < "{to_date}" or cd.posting_date > "{from_date}"
							union
							select gp.posting_date,"" as no_nota,gp.name as "Document No",sp2.item,sp2.qty,sp2.rate,sp2.amount,sp2.keterangan from `tabStock Payment` sp left join `tabGold Payment` cd on sp2.parent=gp.name
							where gp.docstatus=1 and gp.customer="{customer}" and (gp.posting_date < "{to_date}" or gp.posting_date > "{from_date}"
							union
							select gp2.posting_date,"" as no_nota,gp2.name as "Document No", "Discount" as item,"1" as qty,"100" as rate, gp2.discount_amount as amount,"" as keterangan from `tabGold Payment` 
							where gp2.docstatus=1 and gp.customer="{customer}" and (gp.posting_date < "{to_date}" or gp.posting_date > "{from_date}"
							order by posting_date
	 """.format(customer=filters.get("customer"),from_date=filters.get(filters.get("from_date")),to_date=filters.get("to_date")),as_dict=1)
	columns= ["Posting Date:Date:150","No Nota:Data:100","Document No:Data:100","Item:Data:125","Qty:Float:100","Rate:Float:100","24K:Float:150","Keterangan:Data:200"]
	return columns, data