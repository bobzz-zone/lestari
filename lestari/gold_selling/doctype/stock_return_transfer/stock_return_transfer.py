# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StockReturnTransfer(Document):
	@frappe.whitelist()
	def get_kpr(self):
		# frappe.msgprint(self.type)
		if self.type == "Keluar":
			if self.customer:
			# 	list_kpr = frappe.db.get_list("Konfirmasi Payment Return",filters={'customer':self.customer,'docstatus':1})
			# else:
			# 	list_kpr = frappe.db.get_list("Konfirmasi Payment Return",filters={'docstatus':1})
				list_kpr = frappe.db.sql("""
					SELECT
					a.name,
					a.docstatus,
					b.name AS child_name,
					b.customer,
					b.subcustomer,
					b.is_out,
					b.item,
					b.tolak_qty,
					b.voucher_type,
					b.voucher_no,
					"Konfirmasi Payment Return Rongsok" AS doctype,
					c.kadar
					FROM
					`tabKonfirmasi Payment Return` a
					JOIN `tabKonfirmasi Payment Return Rongsok` b
						ON a.name = b.parent
					JOIN `tabItem` c
						ON b.item = c.item_code
					WHERE a.`docstatus` = 1
					AND (b.customer = '{0}' OR b.subcustomer = '{1}')
					AND b.`tolak_qty` > 0
					AND b.`is_out` = 0
					UNION
					SELECT
					a.name,
					a.docstatus,
					b.name AS child_name,
					b.customer,
					b.subcustomer,
					b.is_out,
					b.item,
					b.tolak_qty,
					b.voucher_type,
					b.voucher_no,
					"Konfirmasi Payment Return Perhiasan" AS doctype,
					c.kadar
					FROM
					`tabKonfirmasi Payment Return` a
					JOIN `tabKonfirmasi Payment Return Perhiasan` b
						ON a.name = b.`parent`
					JOIN `tabItem` c
						ON b.item = c.item_code
					WHERE a.`docstatus` = 1
					AND (b.customer = '{0}' OR b.subcustomer = '{1}')
					AND b.`tolak_qty` > 0
					AND b.`is_out` = 0
				""".format(self.customer,self.sub_customer),as_dict=1)
				# frappe.msgprint(str(list_kpr))
			for row in list_kpr:
				# frappe.msgprint(str(row))
				# doc = frappe.get_doc("Konfirmasi Payment Return", row.name)
				# for col in doc.detail_perhiasan:
				if row.subcustomer:
					subcustomer = row.subcustomer
				else:
					subcustomer = frappe.db.get_value(row.voucher_type,row.voucher_no,'subcustomer')
				if self.sub_customer:
					if self.sub_customer == subcustomer:
						child = {
							'item': row.item,
							'berat': row.tolak_qty,
							'customer': row.customer,
							'sub_customer': subcustomer,
							# 'kadar':frappe.db.get_value("Item",row.item,'kadar'),
							'kadar':row.kadar,
							'voucher_type': row.voucher_type,
							'voucher_no': row.voucher_no,
							'child_type':row.doctype,
							'child_name':row.child_name
						}
						# if row.doctype == "Konfirmasi Payment Return Perhiasan":
						# 	child['child_name'] = row.perhiasan
						# 	frappe.msgprint(str(child))
						# else:
						# 	child['child_name'] = row.rongsok
						# 	frappe.msgprint(str(child))

						self.append("transfer_details",child)
				else:
					child = {
							'item': row.item,
							'berat': row.tolak_qty,
							'customer': row.customer,
							'sub_customer': subcustomer,
							# 'kadar':frappe.db.get_value("Item",row.item,'kadar'),
							'kadar':row.kadar,
							'voucher_type': row.voucher_type,
							'voucher_no': row.voucher_no,
							'child_type':row.doctype,
							'child_name':row.child_name
					}
					# if row.doctype == "Konfirmasi Payment Return Perhiasan":
					# 	child['child_name'] = row.perhiasan
					# 	frappe.msgprint(str(child))
					# else:
					# 	child['child_name'] = row.rongsok
					# 	frappe.msgprint(str(child))

					self.append("transfer_details",child)
				# for col in doc.detail_rongsok:
					# subcustomer = frappe.db.get_value(col.voucher_type,col.voucher_no,'subcustomer')
					# rongsok = {
					# 	'item': col.item,
					# 	'berat': col.tolak_qty,
					# 	'customer': col.customer,
					# 	'sub_customer': subcustomer,
					# 	'kadar':frappe.db.get_value("Item",col.item,'kadar'),
					# 	'voucher_type': col.voucher_type,
					# 	'voucher_no': col.voucher_no,
					# 	'child_type':col.doctype,
					# 	'child_name':col.name,
					# }
					# self.append("transfer_details",rongsok)
		else:
			doc = frappe.get_doc("Stock Return Transfer",self.no_doc)
			self.sales = doc.sales
			self.warehouse = doc.warehouse
			self.customer = doc.customer
			self.sub_customer = doc.sub_customer
			for row in doc.transfer_details:
				details = {
							'item': row.item,
							'berat': row.berat,
							'customer': row.customer,
							'sub_customer': row.sub_customer,
							'kadar':row.kadar,
							'kategori':row.kategori,
							'voucher_type': row.voucher_type,
							'voucher_no': row.voucher_no,
							'child_type':row.child_type,
							'child_name':row.child_name,
						}
				self.append("transfer_details",details)
			# list_kpr = frappe.db.get_list("Stock Return Transfer",filters={'sales':self.sales,'type':"Keluar"})
			# for row in list_kpr:
			# 	doc = frappe.get_doc("Stock Return Transfer", row)
			# 	for col in doc.transfer_detail:
			# 		frappe.db.set_value(str(row.child_type),row.child_name,'is_out',0) 
	def on_submit(self):
		for row in self.transfer_details:
			if self.type == "Keluar":
				frappe.db.set_value(str(row.child_type),row.child_name,'is_out',1)
				# frappe.msgprint(str(frappe.db.get_value(str(row.child_type),row.child_name,'is_out')))
			else:
				frappe.db.set_value(str(row.child_type),row.child_name,'is_out',0)
				# frappe.msgprint(str(frappe.db.get_value(str(row.child_type),row.child_name,'is_out')))
	def on_cancel(self):
		for row in self.transfer_details:
			if self.type == "Keluar":
				frappe.db.set_value(str(row.child_type),row.child_name,'is_out',0)
				# frappe.msgprint(str(frappe.db.get_value(str(row.child_type),row.child_name,'is_out')))