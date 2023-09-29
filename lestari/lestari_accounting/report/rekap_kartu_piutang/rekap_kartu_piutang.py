# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = ["Customer:Link/Customer:200","Deposit IDR:Currency:200","Total Piutang Emas:Float:150","Titipan Emas:Float:150"], []
	data_temp = frappe.db.sql("""select customer,sum(deposit_idr),sum(outstanding) from (SELECT
            customer,
            "0" AS deposit_idr,
            outstanding
            FROM
            `tabGold Invoice`
            WHERE docstatus = 1
            UNION
            SELECT
            customer,
            idr_left AS deposit_idr,
            gold_left*-1 AS outstanding
            FROM
            `tabCustomer Deposit`
            WHERE docstatus = 1) a group by a. customer """, as_list=1)
	for row in data_temp:
		if row[2]<0:
			data.append([row[0],row[1],0,row[2]*-1])
		else:
			data.append([row[0],row[1],row[2],0])
	return columns, data
