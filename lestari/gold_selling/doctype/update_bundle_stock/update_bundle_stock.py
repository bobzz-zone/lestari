# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime ,now
from frappe.model.document import Document
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from frappe.utils import flt

class UpdateBundleStock(Document):
	def on_submit(self):
		ste = frappe.new_doc("Stock Entry")
		# frappe.msgprint(str(ste))
		ste.stock_entry_type = "Material Transfer"
		ste.employee_id = self.pic
		ste.remarks = self.keterangan
		ste.update_bundle_stock_no = self.name
		for items in self.items:
			baris_baru = {
				'item_code' : items.item,
				's_warehouse' : self.s_warehouse,
				't_warehouse' : self.warehouse,
				'qty' : items.qty_penambahan,
				'allow_zero_valuation_rate' : 1
			}
			ste.append("items",baris_baru)
		ste.flags.ignore_permissions = True
		ste.save()
		frappe.msgprint(str(frappe.get_last_doc("Stock Entry")))
	@frappe.whitelist()
	def add_row_action(self):
		baris_baru = {
      				"kadar":self.kadar,
                	"sub_kategori":self.category,
                   	"kategori":frappe.get_doc('Item Group',self.category).parent_item_group,
                    "qty_penambahan":self.bruto
                    }
		self.append("items",baris_baru)
		self.kadar = ""
		self.category = ""
		self.bruto = ""
	@frappe.whitelist()
	def get_bundle_sales(self):
		bundle = frappe.db.get_list("Close Bundle Stock")
		for row in bundle:
			frappe.msgprint(row)
	
@frappe.whitelist()
def get_sub_item(kadar, sub_kategori):
    item_code = frappe.db.sql("""
                              SELECT item_code, gold_selling_item FROM `tabItem` WHERE kadar = "{}" and item_group = "Pembayaran" and item_code LIKE "{}%" LIMIT 1
                              """.format(kadar,sub_kategori))
    # frappe.msgprint(item_code)
    return item_code