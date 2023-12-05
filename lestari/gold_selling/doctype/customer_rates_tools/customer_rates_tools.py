# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CustomerRatesTools(Document):
	@frappe.whitelist(allow_guest=True)
	def reset_form(self):
		self.customer = ""
		self.type = ""
		self.type_emas = ""
		self.kadar = ""
		self.valid_from = ""
		self.items = {}
	@frappe.whitelist(allow_guest=True)
	def get_customer_rates(self):
		# item_group = {}
		# if self.type == 'Buying':
		# 	item_group = frappe.db.get_list('Item Group', filters={'parent_item_group':'Pembayaran'})
		# else:
		# 	item_group = frappe.db.get_list('Item Group', filters={'parent_item_group':'Products','penjualan':1}, order_by="name ASC")
		# for row in item_group:
		# 	# frappe.msgprint(str(row))
		# 	baris_baru = {
		# 		'kategori':row.name,
		# 		'valid_from': self.valid_from
		# 	}
		# 	self.append('items',baris_baru)
		# cr = frappe.db.sql("""
		# 	SELECT
		# 	a.name,
		# 	a.customer,
		# 	a.type,
		# 	a.type_emas,
		# 	a.item,
		# 	a.customer_type,
		# 	a.valid_from,
		# 	a.nilai_tukar,
		# 	a.category,
		# 	b.kadar,
		# 	b.item_group  
		# 	FROM `tabCustomer Rates` a
		# 	JOIN `tabGold Selling Item` b
		# 	ON a.category = b.name
		# 	WHERE a.customer = '{0}'
		# 	AND a.type = '{1}'
		# 	AND a.type_emas = '{2}' 
		# 	AND b.kadar = '{3}'
		# 	""".format(self.customer,self.type,self.type_emas,self.kadar),as_dict=1)
		# # self.items = {}
		# for row in cr:
		# 	baris_baru = {
		# 		'kategori': row.item_group,
		# 		'item': row.item,
		# 		'rate': row.nilai_tukar,
		# 		'customer_type': row.customer_type,
		# 		'id_rates': row.name,
		# 		'valid_from': row.valid_from,
		# 		'gold_selling_item':row.category
		# 	}
		# 	self.append('items',baris_baru)
