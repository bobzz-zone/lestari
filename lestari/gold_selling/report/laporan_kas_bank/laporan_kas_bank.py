# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	
	columns = [
	"Name:Link/GL Entry:150",
	"Keterangan:Data:150",
	"Cost Center:Link/Cost Center:150",
	"Remarks:Data:150",
	"Debit:Link/Account:150",
	"Credit:Link/Account:150",
	"Masuk:Data:150",
	"Keluar:Data:150",
	"Saldo:Data:150",
	"Proses:Data:150",
	"Penyebab:Data:150",
	"Dok No:Data:150",
	]
	conditional = []
	# if filters.status:
	# 	conditional.append("po.status = '{}'".format(filters.status))
	# if filters.id: 
	# 	conditional.append("po.name = '{}'".format(filters.id))
	# if filters.supplier:
	# 	conditional.append("po.supplier = '{}'".format(filters.supplier))
	if filters.from_date:
		conditional.append("posting_date BETWEEN '{}' AND '{}'".format(filters.from_date,filters.to_date))
	data = frappe.db.sql("""SELECT 
	gl.name,
	acc.account_name,
	gl.cost_center,
	gl.remarks,
	gl.account,
	gl.against,
	# gl.debit_in_account_currency,
	# gl.credit_in_account_currency
	CONCAT(cur.`symbol`," ", FORMAT(gl.`debit_in_account_currency`,2) ),
	CONCAT(cur.`symbol`," ", FORMAT(gl.`credit_in_account_currency`,2) ),
	CONCAT(cur.`symbol`," ", FORMAT(0,2) ),
	'',
	gl.voucher_type,
	gl.voucher_no
	FROM `tabGL Entry` gl
	JOIN `tabAccount` acc ON acc.name = gl.account
	JOIN `tabCurrency` cur ON cur.name = gl.account_currency
	WHERE 
 	{0}
	ORDER BY
	gl.voucher_no
			 """.format(' AND '.join(conditional)))
	return columns, data
