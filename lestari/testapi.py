import frappe
import json
from frappe.utils import flt
# @frappe.whitelist()
#     response = json.loads(str(resep))
#     # response = frappe.new_doc("Resep Mul Karet")
#     # response.rubber_mould = "KCCWBMT-10003"
#     # response.final_product = "?"
#     # response.type_mul =
#     return response

def fix_outstanding():
	data = frappe.db.sql("select name,grand_total from `tabGold Invoice` where docstatus=1",as_list=1)
	for row in data:
		payment = frappe.db.sql("select sum(allocated) as total from `tabGold Payment Invoice` where gold_invoice='{}' and docstatus=1 group by gold_invoice ".format(row[0]),as_list=1)
		#update
		if payment and len(payment)>0:
			frappe.db.sql("update `tabGold Invoice` set outstanding={} where name='{}'".format(flt(row[1])-flt(payment[0][0]),row[0]),as_list=1)

def fix_mr():
	frappe.db.sql("update `tabMaterial Request Item` set ordered_qty=0 where docstatus=0")
	data = frappe.db.sql("select name from `tabMaterial Request` where docstatus=1 and material_request_type='Purchase'",as_list=1)
	for row in data:
		mr = frappe.get_doc("Material Request",row[0])
		mr.update_completed_qty()
		frappe.db.commit()
def test_patch():
    list_gp = frappe.db.sql("select name from `tabGold Payment` where docstatus=1",as_list=1)
    for row in list_gp:
        no_doc=row[0]
        frappe.db.sql("delete from `tabGL Entry` where voucher_no='{}' and voucher_type='Gold Payment'".format(no_doc))
        doc = frappe.get_doc("Gold Payment", no_doc)
        doc.make_gl_entries()
        print(no_doc)
        frappe.db.commit()
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

@frappe.whitelist()
def item_form_order(item=None):
    item = json.loads(item)
    doc = frappe.new_doc("Form Order")
    for row in item:
        baris_baru = {
            "model" : row,
            "item_name" : frappe.db.get_value("Item",row,'item_name'),
            "kadar" : frappe.db.get_value("Item",row,'kadar'),
            "sub_kategori" : frappe.db.get_value("Item",row,'item_group'),
            "kategori" : frappe.db.get_value("Item",row,'item_group_parent'),
            "kategori_pohon" : frappe.db.get_value("Item",row,'kategori_pohon'),
            "qty_isi_pohon" : frappe.db.get_value("Item",row,'qty_isi_pohon'),
            "image" : frappe.db.get_value("Item",row,'image'),
        }
        doc.append("items",baris_baru)
    doc.flags.ignore_permissions = True
    doc.save()
    return doc.as_dict()
