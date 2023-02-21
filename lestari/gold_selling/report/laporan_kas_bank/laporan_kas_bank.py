# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from collections import OrderedDict

import frappe
from frappe import _, _dict
from frappe.utils import getdate

from erpnext import get_company_currency, get_default_company

# to cache translations
TRANSLATIONS = frappe._dict()

def execute(filters=None):
	if not filters:
		return [], []
		
	account_details = {}

	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	columns = get_column()
	
	update_translations()

	data = get_result(filters, account_details)

	return columns, data

def update_translations():
	TRANSLATIONS.update(
		dict(OPENING=_("Opening"), TOTAL=_("Total"), CLOSING_TOTAL=_("Closing (Opening + Total)"))
	)

def validate_filters(filters, account_details):
	if not filters.get("from_date") and not filters.get("to_date"):
		frappe.throw(
			_("{0} and {1} are mandatory").format(frappe.bold(_("From Date")), frappe.bold(_("To Date")))
		)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def get_result(filters, account_details):
	gl_entries = get_gl_entries(filters)

	data = get_data_with_opening_closing(filters, account_details, gl_entries)

	result = get_result_as_list(data, filters)

	return result

def get_gl_entries(filters):
	# gl_entries = frappe.db.sql(
	# 	"""
	# 	SELECT 
	# 		gl.name as gl_entry,
	# 		gl.posting_date,
	# 		acc.account_name as buku,
	# 		gl.cost_center,
	# 		gl.remarks as keterangan,
	# 		gl.account,
	# 		gl.against,
	# 		gl.debit_in_account_currency,
	# 		gl.credit_in_account_currency,
	# 		gl.voucher_type,
	# 		gl.voucher_no
	# 		FROM `tabGL Entry` gl
	# 		JOIN `tabAccount` acc ON acc.name = gl.account
	# 		JOIN `tabCurrency` cur ON cur.name = gl.account_currency
	# 	WHERE is_cancelled = 0
	# 	{conditions}
	# 	ORDER BY gl.voucher_no
	# 	""".format(
	# 		conditions=get_conditions(filters),
	# 	),
	# 	filters
	# )

	gl_entries = frappe.db.sql("""
		SELECT 
			name as gl_entry, posting_date, (select account_name from `tabAccount` where name = account) as buku, cost_center,
			remarks as keterangan, account, against,
			debit, credit,
			voucher_type, voucher_no
			FROM `tabGL Entry`
		WHERE is_cancelled = 0
		{conditions}
		order by posting_date, voucher_type, voucher_no
	""".format(
			conditions=get_conditions(filters),
		),
		filters, as_dict=1, debug=1
	)

	return gl_entries

def get_conditions(filters):
	conditions = []

	# if filters.name:
	# 	conditions.append("gl.name = %(name)s")
	# if filters.against: 
	# 	conditions.append("gl.against = %(against)s")
	# if filters.account:
	# 	conditions.append("gl.account = '{}'".format(filters.account))
	# if filters.cost_center:
	# 	conditions.append("gl.cost_center = '{}'".format(filters.cost_center))

	conditions.append("(posting_date <=%(to_date)s or is_opening = 'Yes')")

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_data_with_opening_closing(filters, account_details, gl_entries):
	data = []

	gle_map = initialize_gle_map(gl_entries, filters)

	totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)

	# Opening for filtered account
	data.append(totals.opening)

	data += entries

	# totals
	data.append(totals.total)

	# closing
	data.append(totals.closing)

	return data

def get_totals_dict():
	def _get_debit_credit_dict(label):
		return _dict(
			buku="{0}".format(label),
			debit=0.0,
			credit=0.0,
			debit_in_account_currency=0.0,
			credit_in_account_currency=0.0,
		)

	return _dict(
		opening=_get_debit_credit_dict(TRANSLATIONS.OPENING),
		total=_get_debit_credit_dict(TRANSLATIONS.TOTAL),
		closing=_get_debit_credit_dict(TRANSLATIONS.CLOSING_TOTAL),
	)

def initialize_gle_map(gl_entries, filters):
	gle_map = OrderedDict()

	for gle in gl_entries:
		gle_map.setdefault(gle.get('account'), _dict(totals=get_totals_dict(), entries=[]))
	return gle_map

def get_accountwise_gle(filters, gl_entries, gle_map):
	totals = get_totals_dict()
	entries = []
	consolidated_gle = OrderedDict()

	def update_value_in_dict(data, key, gle):
		data[key].debit += gle.debit
		data[key].credit += gle.credit

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	
	for gle in gl_entries:
		group_by_value = gle.get('account')
		if gle.posting_date < from_date:
			update_value_in_dict(totals, "opening", gle)
			update_value_in_dict(totals, "closing", gle)
		elif gle.posting_date <= to_date:
			keylist = [
				gle.get("voucher_type"),
				gle.get("voucher_no"),
				gle.get("account")
			]

			key = tuple(keylist)
			if key not in consolidated_gle:
				consolidated_gle.setdefault(key, gle)
			else:
				update_value_in_dict(consolidated_gle, key, gle)
	
	for key, value in consolidated_gle.items():
		update_value_in_dict(totals, "total", value)
		update_value_in_dict(totals, "closing", value)
		entries.append(value)

	return totals, entries

def get_result_as_list(data, filters):
	balance, balance_in_account_currency = 0, 0

	for d in data:
		if not d.get("posting_date"):
			balance, balance_in_account_currency = 0, 0

		balance = get_balance(d, balance, "debit", "credit")
		d["balance"] = balance

	return data

def get_balance(row, balance, debit_field, credit_field):
	balance += row.get(debit_field, 0) - row.get(credit_field, 0)

	return balance

def get_column():
	company = get_default_company()
	currency = get_company_currency(company)

	columns = [
		{
			"label": _("ID"),
			"fieldname": "gl_entry",
			"fieldtype": "Link",
			"options": "GL Entry",
			"width": 150
		},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 90},
		{
			"label": _("Buku"), 
			"fieldname": "buku", 
			"fieldtype": "Data", 
			"width": 150
		},
		{
			"label": _("Cost Center"),
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 150
		},
		{
			"label": _("Keterangan"), 
			"fieldname": "keterangan", 
			"fieldtype": "Data", 
			"width": 150
		},
		{
			"label": _("Debit"), 
			"fieldname": "account", 
			"fieldtype": "Link",
			"options": "Account",
			"width": 150
		},
		{
			"label": _("Credit"), 
			"fieldname": "against", 
			"fieldtype": "Link",
			"options": "Account",
			"width": 150
		},
		{
			"label": _("Masuk ({0})").format(currency),
			"fieldname": "debit",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Keluar ({0})").format(currency),
			"fieldname": "credit",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Saldo ({0})").format(currency),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Proses"), 
			"fieldname": "proses", 
			"fieldtype": "Data", 
			"width": 150
		},
		{
			"label": _("Penyebab"), 
			"fieldname": "voucher_type", 
			"fieldtype": "Data", 
			"width": 150
		},
		{
			"label": _("Dok No"), 
			"fieldname": "voucher_no", 
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 150
		},
	]
	# columns = [
	# 	"Name:Link/GL Entry:150",
	# 	"Keterangan:Data:150",
	# 	"Cost Center:Link/Cost Center:150",
	# 	"Remarks:Data:150",
	# 	"Debit:Link/Account:150",
	# 	"Credit:Link/Account:150",
	# 	"Masuk:Data:150",
	# 	"Keluar:Data:150",
	# 	"Saldo:Data:150",
	# 	"Proses:Data:150",
	# 	"Penyebab:Data:150",
	# 	"Dok No:Data:150",
	# ]

	return columns