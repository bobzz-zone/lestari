import frappe
import json
@frappe.whitelist()
    response = json.loads(str(resep))
    # response = frappe.new_doc("Resep Mul Karet")
    # response.rubber_mould = "KCCWBMT-10003"
    # response.final_product = "?"
    # response.type_mul =
    return response

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_item_group(doctype, txt, searchfield, start, page_len, filters=None):
    frappe.msgprint('masukpython')
	select = frappe.db.sql("""
        SELECT name, 
        item_group,
        item_name,
        item_code,
        kadar,
        qty_isi_pohon,
        weight_per_unit
        FROM `tabItem` 
        WHERE item_group IN (
            SELECT 
            name 
            FROM `tabItem Group` 
            WHERE parent_item_group IN (
                SELECT name FROM `tabItem Group` WHERE old_parent = '{}'
            )
        )		
		""".format(filters.get('item_group')), {
		# 'txt': "%{}%".format(txt),
		# '_txt': txt.replace("%", ""),
		'start': start,
		'page_len': page_len
	})
    frappe.msgprint(str(select))
    return select