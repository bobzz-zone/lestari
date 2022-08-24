# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _
from frappe.model.document import Document

class RPHCBL(Document):
	@frappe.whitelist()
	def get_current_stock(self):
		stock = frappe.get_list('Bin', filters={'warehouse': 'Campur Bahan - L'}, fields=['warehouse', 'actual_qty', 'item_code'], order_by='item_code')
		# frappe.msgprint(str(stock))
		stock_level = ''
		for row in stock:
			# frappe.msgprint(str(row.item_code))
			qty = flt(row.actual_qty) * 0.1
			# self.set('stock_level','<div class="progress" style="margin-bottom:25px"><div class="progress-bar" role="progressbar" style="width: '+str(qty)+'%;">'+str(qty)+'%</div></div>')
			stock_level += '<div class="col-lg-12">'+row.item_code+'</div><div class="progress" style="margin-bottom:25px"><div class="progress-bar text-warning" role="progressbar" style="width: '+str(qty)+'%;min-width:2em;">'+str(row.actual_qty)+'</div></div>'
		return stock_level
	# pass

			
			
