# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, nowdate
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname
import erpnext
from datetime import datetime



class PurchaseReceipt(BuyingController):
    @frappe.whitelist()
    def autoname_prec(self,method):

        if self.naming_series != '###/01NIC/EIQ/#M#/#Y#':
            # self.quotation_owner = frappe.session.user
            return

        naming_series = self.naming_series
        kode = "XXXX"
        
        if not self.quotation_owner:
            frappe.throw('Quottation Owner is required')

        kode_list = frappe.db.sql(""" 
                        SELECT CONCAT(kode_sales_person,inisial_name) 
                        FROM tabSales Person WHERE name = '{}' and enabled = 1  """.format(self.quotation_owner))

        if kode_list:
            if kode_list[0]:
                if kode_list[0][0]:
                    kode = kode_list[0][0]

        naming_series = self.naming_series.replace("01NIC", kode)

        tahun = str(self.transaction_date).split("-")[0]
        bulan_angka = str(self.transaction_date).split("-")[1]
        
        text_angka = series_estica(naming_series, 3)

        self.name = naming_series.replace("#Y#", tahun).replace("#M#", bulan_romawi(bulan_angka)).replace("###",text_angka)