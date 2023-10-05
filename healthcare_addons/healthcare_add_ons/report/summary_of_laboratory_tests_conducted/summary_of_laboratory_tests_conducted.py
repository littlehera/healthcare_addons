# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	report_type = filters.get("report_type")
	#columns, data = [], []


	columns = get_columns(report_type)

	if report_type == "Total Only":
		data = get_data(from_date, to_date)
	else:
		data = get_data1(from_date, to_date)

	return columns, data

def get_columns(report_type):
	if report_type == "Total Only":
		columns = [
			{"label": "Item", 'width': 150, "fieldname": "item_name"},
			{"label": "Total Qty", 'width': 150, "fieldname": "qty"},
		]
	else:
		columns = [
			{"label": "Item", 'width': 150, "fieldname": "item_name"},
			{"label": "Doctor's Referral- Regular", 'width': 150, "fieldname": "dr_ref_reg"},
			{"label": "Doctor's Referral- SC/PWD", 'width': 150, "fieldname": "dr_ref_sc"},
			{"label": "Doctor's Referral- MD", 'width': 150, "fieldname": "dr_ref_md"},
			{"label": "Walk-in-Regular", 'width': 150, "fieldname": "wlkin_reg"},
			{"label": "Walk-in- SC/PWD", 'width': 150, "fieldname": "wlkin_sc"},
			{"label": "Walk-in- MD", 'width': 150, "fieldname": "wlkin_md"},
			{"label": "HMO", 'width': 150, "fieldname": "hmo"},
			{"label": "Company", 'width': 150, "fieldname": "company"},
			{"label": "Package", 'width': 150, "fieldname": "package"},
			{"label": "Promo", 'width': 150, "fieldname": "promo"},
			{"label": "Employee Benefit", 'width': 150, "fieldname": "emp_bnft"},
		]

	return columns

def get_data1(from_date, to_date):
	data = []
	items = frappe.db.sql("""SELECT name, item_name from `tabItem` where item_group = 'Laboratory'""")
	sources = [
			{"label": "Doctor's Referral- Regular", 'width': 150, "fieldname": "dr_ref_reg"},
			{"label": "Doctor's Referral- SC/PWD", 'width': 150, "fieldname": "dr_ref_sc"},
			{"label": "Doctor's Referral- MD", 'width': 150, "fieldname": "dr_ref_md"},
			{"label": "Walk-in-Regular", 'width': 150, "fieldname": "wlkin_reg"},
			{"label": "Walk-in- SC/PWD", 'width': 150, "fieldname": "wlkin_sc"},
			{"label": "Walk-in- MD", 'width': 150, "fieldname": "wlkin_md"},
			{"label": "HMO", 'width': 150, "fieldname": "hmo"},
			{"label": "Company", 'width': 150, "fieldname": "company"},
			{"label": "Package", 'width': 150, "fieldname": "package"},
			{"label": "Promo", 'width': 150, "fieldname": "promo"},
			{"label": "Employee Benefit", 'width': 150, "fieldname": "emp_bnft"}
	]
	for item in items:
		item_details = {}
		item_details['item_name'] = item[1]
		item_details['item_code'] = item[0]
		if not is_product_bundle(item[0]):
			for row in sources:
				si_qty = get_si_item_total(from_date, to_date, item[0],row['label'])
				bundle_qty = get_bundle_item_total(from_date, to_date, item[0], row['label'])
				total_qty = si_qty + bundle_qty
				item_details[row['fieldname']]=total_qty
			data.append(item_details)
	return data

def get_data(from_date, to_date):
	data = []
	items = frappe.db.sql("""SELECT name, item_name from `tabItem` where item_group = 'Laboratory'""")
	for item in items:
		total_qty = 0
		item_code = item[0]
		item_name = item[1]
		si_qty = get_si_item_total(from_date, to_date, item_code)
		bundle_qty = get_bundle_item_total(from_date, to_date, item_code)
		total_qty = si_qty + bundle_qty
		if total_qty > 0 and not is_product_bundle(item_code):
			data.append({"item_name":item_name,"qty":total_qty})
	return data

def get_si_item_total(from_date, to_date, item_code, si_source = None):

	source = si_source if si_source is not None else ""

	qty = frappe.db.sql("""SELECT SUM(itm.qty) from `tabSales Invoice Item` itm join `tabSales Invoice` si on
					 		si.name = itm.parent where itm.item_code = %s and si.docstatus = 1 and si.posting_date >=%s
					 		and si.posting_date<=%s and si.custom_source like %s""",(item_code, from_date, to_date, '%'+source+'%'))
	if len(qty)<1:
		return 0
	else:
		return qty[0][0] if qty[0][0] is not None else 0


def get_bundle_item_total(from_date, to_date, item_code, si_source = None):

	source = si_source if si_source is not None else ""
	
	qty = frappe.db.sql("""SELECT SUM(itm.qty) from `tabPacked Item` itm join `tabSales Invoice` si on
					 		si.name = itm.parent where itm.item_code = %s and si.docstatus = 1 and si.posting_date >=%s
					 		and si.posting_date<=%s and si.custom_source like %s """,(item_code, from_date, to_date, '%'+source+'%'))
	if len(qty)<1:
		return 0
	else:
		return qty[0][0] if qty[0][0] is not None else 0

def is_product_bundle(item_code):
	count_item = frappe.db.sql("""SELECT count(*) from `tabProduct Bundle` where new_item_code = %s""",item_code)[0][0]
	return True if (count_item is not None and count_item > 0) else False