# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	columns, data = [], []
	#saldo awal

	#mutasi
	log_data = frappe.db.sql("""select date, voucher_type,voucher_no , item,bruto,rate,netto from `tabGold Log` 
		where customer="{}" and date <= "{}" and date >="{}"
	 """.format(filters.get("customer"),filters.get("to_date"),filters.get("from_date")))
	return columns, data
