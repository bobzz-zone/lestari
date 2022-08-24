# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TransferMaterial(Document):
	pass

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_nthko(doctype, txt, searchfield, start, page_len, filters=None):
	return frappe.db.sql("""
			SELECT 
			name, module
			FROM `tabDocType`
			WHERE TRUE
			AND module = "{}"
			AND is_submittable = "{}"
			AND name LIKE "{}"			
		""".format(filters.get("module"),filters.get('is_submittable'),filters.get('name')))
