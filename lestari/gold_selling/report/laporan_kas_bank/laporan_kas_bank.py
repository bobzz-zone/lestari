# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	
	columns = [
	"Name:Link/GL Entry:150",
	"Account:Link/Account:150",
	"Cost Center:Link/Cost Center:150",
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
	name,
	account,
	cost_center
	# CONCAT(po.`currency`," ", FORMAT(poi.`rate`,2) ),
	# CONCAT(po.`currency`," ", FORMAT(poi.`net_amount`,2) ),
	# CONCAT(po.`currency`," ", FORMAT(po.`grand_total`,2) ),
	FROM `tabGL Entry`
	WHERE 
 	{0}
			 """.format(' AND '.join(conditional)))
	return columns, data
