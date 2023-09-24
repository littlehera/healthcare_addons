# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	totals_only = filters.get("totals_only")
	report_type = filters.get("report_type")

	#frappe.msgprint("TOTALS ONLY="+str(totals_only))

	columns = get_columns(totals_only, report_type)
	data = get_data(from_date, to_date, totals_only, report_type)
	return columns, data

def get_columns(totals_only, report_type):

	if totals_only != 1:
		columns = [
			{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
			{"label": "Posting Date", 'width': 350, "fieldname": "posting_date"},
			{"label": "Source", 'width': 150, "fieldname": "si_source"},
			{"label": "Referred By", 'width': 150, "fieldname": "ref_practitioner"},
			{"label": "Gross Total", 'width': 150, "fieldname": "gross_total", "fieldtype":"Currency", "precision":2},
			{"label": "Discount %", 'width': 150, "fieldname": "disc_perc", "fieldtype":"Float", "precision":2},
			{"label": "Discount Amount", 'width': 150, "fieldname": "disc_amount", "fieldtype":"Currency", "precision":2},
			{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
			{"label": "Form of Payment", 'width': 150, "fieldname": "payment_modes"}
		]
	else:
		if report_type == "With subtotals based on Source":
			columns = [
				{"label": "Source", 'width': 150, "fieldname": "si_source"},
				{"label": "Gross Total", 'width': 150, "fieldname": "gross_total", "fieldtype":"Currency", "precision":2},
				{"label": "Discount Amount", 'width': 150, "fieldname": "disc_amount", "fieldtype":"Currency", "precision":2},
				{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
			]
		elif report_type == "with Subtotal for each Form of Payment":
			columns = [
				{"label": "Mode of Payment", 'width': 150, "fieldname": "payment_mode"},
				{"label": "Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2},
			]
		else:
			columns = [
				{"label": "Referred By", 'width': 150, "fieldname": "referred_by"},
				{"label": "Gross Total", 'width': 150, "fieldname": "gross_total", "fieldtype":"Currency", "precision":2},
				{"label": "Discount Amount", 'width': 150, "fieldname": "disc_amount", "fieldtype":"Currency", "precision":2},
				{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
			]

	return columns

def get_data(from_date, to_date, totals_only, report_type):
	#REPORT TYPES: "With subtotals based on Source", "with Subtotal for each Form of Payment","Summary based on Referred By"
	
	# if totals_only == 1:
	# 	group_by = ""
	# 	if report_type =="With subtotals based on Source":
	
	data = []

	rows = frappe.db.sql("""SELECT si.*, payments.payment_mode, payments.amount from `tabSales Invoice` si left join `tabInvoice Payment Table` payments on si.name=payments.parent
					  where si.posting_date >=%s and si.posting_date<=%s and si.docstatus = 1""",(from_date,to_date), as_dict = True)
	for row in rows:
		row['sales_invoice'] = row['name']
		data.append(row)
	
	return data
