# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
import json
import os
import requests
from frappe.model.document import Document

class WhatsappSetting(Document):
	@frappe.whitelist()
	def get_template(self):
		host = "https://graph.facebook.com"
		path = "/{}/{}/message_templates?fields=name,category,components,language,name_or_content,status".format(self.version,self.waba_id)
		url = str(host+path)
		headers = {
			'Content-Type': 'application/json',
			'Authorization': 'Bearer {}'.format(self.user_access_token)
		}
		resp = requests.request("GET",url,headers=headers, allow_redirects=False)
		ret = json.loads(resp.text)
		frappe.msgprint(str(ret))
		for row in ret['data']:
			if not frappe.db.exists("Whatsapp Template", row['id']):
				template = frappe.new_doc("Whatsapp Template")
				template.id_template = row['id']
				template.language = row['language']
				template.name_template = row['name']
				template.category = row['category']
				template.status = row['status']
				component_list = []
				for component in row['components']:
					component_list.append({

					})
				template.components = component_list
				template.save(ignore_permissions=True)


