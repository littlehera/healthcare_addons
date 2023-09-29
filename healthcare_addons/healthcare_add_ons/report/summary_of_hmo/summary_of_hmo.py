# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	hmo = filters.get("hmo") if filters.get("hmo")is not None else ""
	report_type = filters.get("report_type")

	columns = [
		{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
		{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
		{"label": "HMO", 'width': 150, "fieldname": "hmo"},
		{"label": "Item", 'width': 150, "fieldname": "item_name"},
		{"label": "Qty", 'width': 150, "fieldname": "qty"},
		{"label": "Rate", 'width': 150, "fieldname": "rate"},
		{"label": "Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2}
	]

	data = get_data(from_date, to_date, report_type, hmo)

	return columns, data



def get_data(from_date, to_date, report_type, hmo):
	data = []
	if report_type == 'Laboratory Tests':
		data = frappe.db.sql("""SELECT si.name as sales_invoice, si.posting_date, si.custom_hmo as hmo, itm.item_name, itm.qty, itm.rate, 
					   			itm.amount from `tabSales Invoice` si
					   			join `tabSales Invoice Item` itm on itm.parent = si.name where si.posting_date >= %s and si.posting_date<=%s and
					   			si.docstatus = 1 and si.custom_hmo like %s and itm.item_code in (select name from `tabItem` where item_group = 'Laboratory')""",
								(from_date, to_date, '%'+hmo+'%'),as_dict = True)
	else:
		data = frappe.db.sql("""SELECT si.name as sales_invoice, si.posting_date, si.custom_hmo as hmo, itm.item_name, itm.qty, itm.rate, 
					   			itm.amount from `tabSales Invoice` si
					   			join `tabSales Invoice Item` itm on itm.parent = si.name where si.posting_date >= %s and si.posting_date<=%s and
					   			si.docstatus = 1 and si.custom_hmo like %s and itm.item_code in (select name from `tabItem` where item_group = 'Services')""",
								(from_date, to_date, '%'+hmo+'%'),as_dict = True)
	
	return data