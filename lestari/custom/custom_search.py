# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# Search
from __future__ import unicode_literals

import json
import re

import wrapt
from six import string_types

import frappe
from frappe import _, is_whitelisted
from frappe.permissions import has_permission
from frappe.translate import get_translated_doctypes
from frappe.utils import cint, cstr, unique
from frappe.desk.search import get_std_fields_list
from frappe.desk.reportview import validate_args
from frappe.model.db_query import check_parent_permission

@frappe.whitelist()
def search_widget(
	doctype,
	txt,
	query=None,
	searchfield=None,
	start=0,
	page_length=20,
	filters=None,
	filter_fields=None,
	as_dict=False,
	reference_doctype=None,
	ignore_user_permissions=False,
):

	start = cint(start)

	if isinstance(filters, string_types):
		filters = json.loads(filters)

	if searchfield:
		sanitize_searchfield(searchfield)

	if not searchfield:
		searchfield = "name"

	standard_queries = frappe.get_hooks().standard_queries or {}

	if query and query.split()[0].lower() != "select":
		# by method
		try:
			is_whitelisted(frappe.get_attr(query))
			frappe.response["values"] = frappe.call(
				query, doctype, txt, searchfield, start, page_length, filters, as_dict=as_dict
			)
		except frappe.exceptions.PermissionError as e:
			if frappe.local.conf.developer_mode:
				raise e
			else:
				frappe.respond_as_web_page(
					title="Invalid Method", html="Method not found", indicator_color="red", http_status_code=404
				)
			return
		except Exception as e:
			raise e
	elif not query and doctype in standard_queries:
		# from standard queries
		search_widget(
			doctype, txt, standard_queries[doctype][0], searchfield, start, page_length, filters
		)
	else:
		meta = frappe.get_meta(doctype)

		if query:
			frappe.throw(_("This query style is discontinued"))
			# custom query
			# frappe.response["values"] = frappe.db.sql(scrub_custom_query(query, searchfield, txt))
		else:
			if isinstance(filters, dict):
				filters_items = filters.items()
				filters = []
				for f in filters_items:
					if isinstance(f[1], (list, tuple)):
						filters.append([doctype, f[0], f[1][0], f[1][1]])
					else:
						filters.append([doctype, f[0], "=", f[1]])

			if filters == None:
				filters = []
			or_filters = []

			translated_doctypes = frappe.cache().hget(
				"translated_doctypes", "doctypes", get_translated_doctypes
			)
			# build from doctype
			if txt:
				field_types = [
					"Data",
					"Text",
					"Small Text",
					"Long Text",
					"Link",
					"Select",
					"Read Only",
					"Text Editor",
				]
				search_fields = ["name"]
				if meta.title_field:
					search_fields.append(meta.title_field)

				if meta.search_fields:
					search_fields.extend(meta.get_search_fields())

				for f in search_fields:
					fmeta = meta.get_field(f.strip())
					if (doctype not in translated_doctypes) and (
						f == "name" or (fmeta and fmeta.fieldtype in field_types)
					):
						or_filters.append([doctype, f.strip(), "like", "%{0}%".format(txt)])

			if meta.get("fields", {"fieldname": "enabled", "fieldtype": "Check"}):
				filters.append([doctype, "enabled", "=", 1])
			if meta.get("fields", {"fieldname": "disabled", "fieldtype": "Check"}):
				filters.append([doctype, "disabled", "!=", 1])

			# format a list of fields combining search fields and filter fields
			fields = get_std_fields_list(meta, searchfield or "name")
			if filter_fields:
				fields = list(set(fields + json.loads(filter_fields)))
			formatted_fields = ["`tab%s`.`%s`" % (meta.name, f.strip()) for f in fields]

			# find relevance as location of search term from the beginning of string `name`. used for sorting results.
			formatted_fields.append(
				"""locate({_txt}, `tab{doctype}`.`name`) as `_relevance`""".format(
					_txt=frappe.db.escape((txt or "").replace("%", "").replace("@", "")), doctype=doctype
				)
			)

			# In order_by, `idx` gets second priority, because it stores link count
			from frappe.model.db_query import get_order_by

			order_by_based_on_meta = get_order_by(doctype, meta)
			# 2 is the index of _relevance column
			order_by = "_relevance, {0}, `tab{1}`.idx desc".format(order_by_based_on_meta, doctype)

			ptype = "select" if frappe.only_has_select_perm(doctype) else "read"
			ignore_permissions = (
				True
				if doctype == "DocType"
				else (cint(ignore_user_permissions) and has_permission(doctype, ptype=ptype))
			)

			if doctype in translated_doctypes:
				page_length = None

			values = frappe.get_list(
				doctype,
				filters=filters,
				fields=formatted_fields,
				or_filters=or_filters,
				limit_start=start,
				limit_page_length=page_length,
				order_by=order_by,
				ignore_permissions=ignore_permissions,
				reference_doctype=reference_doctype,
				as_list=not as_dict,
				strict=False,
			)

			if doctype in translated_doctypes:
				# Filtering the values array so that query is included in very element
				values = (
					v
					for v in values
					if re.search(f"{re.escape(txt)}.*", _(v.name if as_dict else v[0]), re.IGNORECASE)
				)

			# Sorting the values array so that relevant results always come first
			# This will first bring elements on top in which query is a prefix of element
			# Then it will bring the rest of the elements and sort them in lexicographical order
			values = sorted(values, key=lambda x: relevance_sorter(x, txt, as_dict))

			# remove _relevance from results
			if as_dict:
				for r in values:
					r.pop("_relevance")
				frappe.response["values"] = values
			else:
				frappe.response["values"] = [r[:-1] for r in values]

@frappe.whitelist()
def get_list(
	doctype,
	fields=None,
	filters=None,
	order_by=None,
	limit_start=None,
	limit_page_length=None,
	parent=None,
	debug=True,
	as_dict=True,
	or_filters=None,
):
	"""Returns a list of records by filters, fields, ordering and limit

	:param doctype: DocType of the data to be queried
	:param fields: fields to be returned. Default is `name`
	:param filters: filter list by this dict
	:param order_by: Order by this fieldname
	:param limit_start: Start at this index
	:param limit_page_length: Number of records to be returned (default 20)"""
	if frappe.is_table(doctype):
		check_parent_permission(parent, doctype)

	filter = json.loads(filters)

	parent_exist = False
	for row in filter:
		if row[0] != "parent":
			continue

		parent_exist = True

	if not parent_exist:
		return []

	# frappe.msgprint(filters)
	args = frappe._dict(
		doctype=doctype,
		fields=fields,
		filters=filters,
		or_filters=or_filters,
		order_by=order_by,
		# limit_start=limit_start,
		# limit_page_length=limit_page_length,
		debug=debug,
		as_list=not as_dict,
	)

	validate_args(args)
	list_child = frappe.get_list(**args)
	# frappe.msgprint(list_child)
	return list_child