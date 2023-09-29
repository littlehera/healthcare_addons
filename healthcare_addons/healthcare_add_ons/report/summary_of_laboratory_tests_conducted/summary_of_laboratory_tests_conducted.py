# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	#columns, data = [], []

	columns = [
		{"label": "Item", 'width': 150, "fieldname": "item_name"},
		{"label": "Total Qty", 'width': 150, "fieldname": "qty"},
	]
	
	data = get_data(from_date, to_date)

	return columns, data

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

def get_si_item_total(from_date, to_date, item_code):
	qty = frappe.db.sql("""SELECT SUM(itm.qty) from `tabSales Invoice Item` itm join `tabSales Invoice` si on
					 		si.name = itm.parent where itm.item_code = %s and si.docstatus = 1 and si.posting_date >=%s
					 		and si.posting_date<=%s""",(item_code, from_date, to_date))
	if len(qty)<1:
		return 0
	else:
		return qty[0][0] if qty[0][0] is not None else 0


def get_bundle_item_total(from_date, to_date, item_code):
	qty = frappe.db.sql("""SELECT SUM(itm.qty) from `tabPacked Item` itm join `tabSales Invoice` si on
					 		si.name = itm.parent where itm.item_code = %s and si.docstatus = 1 and si.posting_date >=%s
					 		and si.posting_date<=%s""",(item_code, from_date, to_date))
	if len(qty)<1:
		return 0
	else:
		return qty[0][0] if qty[0][0] is not None else 0

def is_product_bundle(item_code):
	count_item = frappe.db.sql("""SELECT count(*) from `tabProduct Bundle` where new_item_code = %s""",item_code)[0][0]
	return True if (count_item is not None and count_item > 0) else False