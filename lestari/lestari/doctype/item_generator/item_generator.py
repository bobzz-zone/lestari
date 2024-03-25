# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ItemGenerator(Document):
	@frappe.whitelist()
	def get_kadar(self):
		item_group_parent = self.item_group_parent
		if self.item_group_gold_selling:
			item_group_parent = self.item_group_gold_selling
		if not self.item_group:
			frappe.throw('Tolong Isi Item Group Terlebih Dahulu.')
   
		kadar = frappe.get_list('Data Logam')
		baris_baru = []
		for row in sorted(kadar, key=lambda x: x.name):
			# frappe.msgprint(item_group_parent)
			# frappe.msgprint(str(frappe.db.get_value('Gold Selling Item',{'kadar' : row.name, 'item_group': item_group_parent }, ['name'])))
			baris_baru.append({
				'kadar' : row.name,
				'gold_selling_item' : frappe.db.get_value('Gold Selling Item',{'kadar' : str(row.name), 'item_group': str(item_group_parent) }, ['name'])
			})
			
		self.set('tabel_kadar', baris_baru)
	def on_submit(self):
		item_code = ''
		if not self.item_code:
			item_code = self.item_code_from_items
			index = item_code.index("-")
			item_code = item_code[:index]
		else:
			item_code = self.item_code
		for row in self.tabel_kadar:
			frappe.msgprint(row.kadar)
			kadar = frappe.db.get_value('Data Logam',{'jenis_logam' : row.kadar }, 'sku')
			alloy = frappe.db.get_value('Data Logam',{'jenis_logam' : row.kadar }, 'alloy')
			item_name = self.item_name
			new = frappe.new_doc('Item')
			new.item_code = item_code+"-"+kadar+alloy
			# index1 = item_name.index("gr") + len("gr")
			# new_item_name = item_name[:index1].strip()
			# new_item_name = item_name.split("06K-300")[0].strip()
			new.item_name = item_name+" "+row.kadar
			new.item_group = self.item_group
			new.item_group_parent = self.item_group_parent
			new.stock_uom = self.default_uom
			new.kategori_pohon = self.kategori_pohon
			new.qty_isi_pohon = self.qty_isi_pohon
			new.kadar = row.kadar
			new.weight_per_unit = row.berat_target
			new.weight_uom = self.uom_berat
			new.barang_yang_dibawa_sales = self.barang_yang_dibawa_sales
			new.gold_selling_item = row.gold_selling_item
			# new.opening_stock = 100
			new.brand = self.logo
			new.description = self.description
			# new.valuation_rate = 0
			new.image = self.image
			new.flags.ignore_permissions = True
			new.save()

