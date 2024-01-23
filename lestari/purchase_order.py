# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, nowdate
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname
import erpnext
from datetime import datetime



class PurchaseOrder(BuyingController):
    @frappe.whitelist()
    def generate_po(self):
        pass