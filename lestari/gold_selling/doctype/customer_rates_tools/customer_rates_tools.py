# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CustomerRatesTools(Document):
	@frappe.whitelist()
	def validate(self):
		for row in self.items:
			if row.id_rates:
				frappe.db.sql("""
					UPDATE `tabCustomer Rates`
					SET
					`item` = '{0}',
					`customer_type` = '{1}',
					`valid_from` = '{2}',
					`nilai_tukar` = '{3}',
					`category` = '{4}'
					WHERE name = '{5}'
					""".format(row.item, row.customer_type, row.valid_from, row.rate, row.gold_selling_item, row.id_rates))
			else:
				if not row.gold_selling_item:
					gold_selling_item = frappe.db.get_value('Gold Selling Item', {'kadar': self.kadar,'item_group':row.kategori}, 'name')
				else:
					gold_selling_item = row.gold_selling_item
				new_doc = frappe.new_doc("Customer Rates")
				new_doc.customer = self.customer
				new_doc.type = self.type
				new_doc.type_emas = self.type_emas
				new_doc.kadar = self.kadar
				new_doc.valid_from = self.valid_from
				new_doc.item = row.item
				new_doc.customer_type = self.customer_type
				new_doc.nilai_tukar = row.rate
				new_doc.category = gold_selling_item
				new_doc.flags.ignore_permissions = True
				new_doc.save()
	@frappe.whitelist(allow_guest=True)
	def reset_form(self):
		self.customer = ""
		self.type = ""
		self.type_emas = ""
		self.kadar = ""
		self.valid_from = ""
		self.customer_type = ""
		self.items = {}
	@frappe.whitelist(allow_guest=True)
	def get_customer_rates(self):
		# pass
		item_group = {}
		if self.type == 'Buying':
			item_group = frappe.db.get_list('Item Group', filters={'parent_item_group':'Pembayaran'})
		else:
			item_group = frappe.db.get_list('Item Group', filters={'parent_item_group':'Products','penjualan':1}, order_by="name ASC")
		for row in item_group:
			# frappe.msgprint(str(row))
			gold_selling_item = frappe.db.get_value('Gold Selling Item', {'kadar': self.kadar,'item_group':row.kategori}, 'name')
			baris_baru = {
				'kategori':row.name,
				'valid_from': self.valid_from,
				'gold_selling_item':gold_selling_item,
			}
			self.append('items',baris_baru)
		cr = frappe.db.sql("""
			SELECT
			a.name,
			a.customer,
			a.type,
			a.type_emas,
			a.item,
			a.customer_type,
			a.valid_from,
			a.nilai_tukar,
			a.category,
			b.kadar,
			b.item_group  
			FROM `tabCustomer Rates` a
			JOIN `tabGold Selling Item` b
			ON a.category = b.name
			WHERE a.customer = '{0}'
			AND a.type = '{1}'
			AND a.type_emas = '{2}' 
			AND b.kadar = '{3}'
			""".format(self.customer,self.type,self.type_emas,self.kadar),as_dict=1)
		if len(cr) > 0:
			self.items = {}
		for row in cr:
			baris_baru = {
				'kategori': row.item_group,
				'item': row.item,
				'rate': row.nilai_tukar,
				'customer_type': row.customer_type,
				'id_rates': row.name,
				'valid_from': row.valid_from,
				'gold_selling_item':row.category
			}
			self.append('items',baris_baru)
