# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from collections import OrderedDict

import frappe
from frappe import _, _dict
from frappe.utils import cstr, getdate,flt

from erpnext import get_company_currency, get_default_company

# to cache translations
TRANSLATIONS = frappe._dict()


def execute(filters=None):
	if not filters:
		return [], []
		
	validate_filters(filters)

	columns = get_column(filters)
	
	update_translations()

	data = get_result(filters)

	return columns, data

def update_translations():
	TRANSLATIONS.update(
		dict(OPENING=_("Opening"), TOTAL=_("Total"), CLOSING_TOTAL=_("Closing (Opening + Total)"))
	)

def validate_filters(filters):
	if not filters.get("account"):
		frappe.throw(
			_("{0} are mandatory").format(frappe.bold(_("Account")))
		)

	if not filters.get("from_date") and not filters.get("to_date"):
		frappe.throw(
			_("{0} and {1} are mandatory").format(frappe.bold(_("From Date")), frappe.bold(_("To Date")))
		)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def get_result(filters):
	gl_entries = get_gl_entries(filters)
	data = get_data_with_opening_closing(filters, gl_entries)

	result = get_result_as_list(data, filters)

	return result

def get_gl_entries(filters):
	gl_entries = frappe.db.sql("""
		SELECT 
			gl.name as gl_entry, gl.posting_date, 
			ifnull(gl.against,gl.voucher_type) as lawan,
			gl.cost_center,
			gl.remarks as keterangan, gl.account as account, gl.against as against,
			gl.debit_in_account_currency as debit , gl.credit_in_account_currency as credit,gl.party,gl.party_type,
			gl.voucher_type, gl.voucher_no
			FROM `tabGL Entry` gl 
		WHERE gl.is_cancelled = 0
		{conditions}
		order by gl.posting_date, gl.voucher_type, gl.voucher_no
	""".format(
			conditions=get_conditions(filters),
		),
		 as_dict=1, debug=1
	)

	return gl_entries
def get_conditions(filters):
	conditions = []

	if filters.account:
		conditions.append(""" gl.is_opening="No" and gl.account = "{0}" """.format(filters.get("account")))
	if filters.party:
		conditions.append(""" gl.party_type="{0}" and gl.party = "{1}" """.format(filters.get("party_type"),filters.get("party")))

	conditions.append(""" gl.posting_date <= "{}" and gl.posting_date >= "{}" """.format(filters.get("to_date"),filters.get("from_date")))

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_data_with_opening_closing(filters, gl_entries):
	data = []
	opening = frappe.db.sql("select sum(debit_in_account_currency -credit_in_account_currency) as total from `tabGL Entry` where (posting_date <'{}'  or is_opening='Yes') and account='{}' and is_cancelled = 0 group by account ".format(filters.get("from_date"),filters.get("account")),as_list=1)
	nilai_opening=0
	if opening:
		nilai_opening=flt(opening[0][0])
	totals, entries = get_accountwise_gle(filters, gl_entries , nilai_opening)

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
			lawan="{0}".format(label),
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

def get_accountwise_gle(filters, gl_entries,opening):
	totals = get_totals_dict()
	entries = []
	consolidated_gle = OrderedDict()

	def update_value_in_dict(data, key, gle):
		data[key].debit += gle.debit
		data[key].credit += gle.credit

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	if opening > 0 :
		totals["opening"].debit += opening
		totals["closing"].debit += opening
	else:
		totals["opening"].credit += opening*-1
		totals["closing"].credit += opening*-1
	for gle in gl_entries:
		group_by_value = gle.get('account')

		if gle.posting_date <= to_date:
			keylist = [
				gle.get("voucher_type"),
				gle.get("voucher_no"),
				gle.get("account"),
				gle.get("gl_entry")
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

def get_column(filters):
	company = get_default_company()
	currency = get_company_currency(company)
	currency_gold = frappe.db.get_value('Account',filters.get("account"),'account_currency')

	columns = [
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
		{
			"label": _("Lawan Transaksi"), 
			"fieldname": "account", 
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
			"label": _("Masuk ({0})").format(currency_gold),
			"fieldname": "debit",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Keluar ({0})").format(currency_gold),
			"fieldname": "credit",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Saldo ({0})").format(currency_gold),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Party Type"), 
			"fieldname": "party_type", 
			"fieldtype": "Data", 
			"width": 150
		},
		{
			"label": _("Party"), 
			"fieldname": "party", 
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
	return columns

