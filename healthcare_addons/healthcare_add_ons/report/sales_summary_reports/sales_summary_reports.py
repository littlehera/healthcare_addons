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
	#REPORT TYPES: "With subtotals based on Source", "with Subtotal for each Form of Payment","Summary based on Referred By"
	if totals_only != 1:
		if report_type in ["With subtotals based on Source", "Summary based on Referred By"]:
			columns = [
				{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
				{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
				{"label": "Source", 'width': 150, "fieldname": "custom_source"},
				{"label": "Referred By", 'width': 150, "fieldname": "custom_practitioner_name"},
				{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
				{"label": "Discount %", 'width': 150, "fieldname": "additional_discount_percentage", "fieldtype":"Float", "precision":2},
				{"label": "Discount Amount", 'width': 150, "fieldname": "discount_amount", "fieldtype":"Currency", "precision":2},
				{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
				{"label": "Form of Payment", 'width': 150, "fieldname": "payment_modes"}
			]
		else:
			columns = [
				{"label": "Form of Payment", 'width': 150, "fieldname": "payment_mode"},
				{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
				{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
				{"label": "Source", 'width': 150, "fieldname": "custom_source"},
				{"label": "Referred By", 'width': 150, "fieldname": "custom_practitioner_name"},
				{"label": "Payment Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2}
				# {"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
				# {"label": "Discount %", 'width': 150, "fieldname": "disc_perc", "fieldtype":"Float", "precision":2},
				# {"label": "Discount Amount", 'width': 150, "fieldname": "disc_amount", "fieldtype":"Currency", "precision":2},
				# {"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
				
			]
	else:
		if report_type == "With subtotals based on Source":
			columns = [
				{"label": "Source", 'width': 150, "fieldname": "custom_source"},
				{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
				{"label": "Discount Amount", 'width': 150, "fieldname": "discount_amount", "fieldtype":"Currency", "precision":2},
				{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
			]
		elif report_type == "with Subtotal for each Form of Payment":
			columns = [
				{"label": "Mode of Payment", 'width': 150, "fieldname": "payment_mode"},
				{"label": "Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2},
			]
		else:
			columns = [
				{"label": "Referred By", 'width': 150, "fieldname": "custom_practitioner_name"},
				{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
				{"label": "Discount Amount", 'width': 150, "fieldname": "discount_amount", "fieldtype":"Currency", "precision":2},
				{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
			]

	return columns

def get_data(from_date, to_date, totals_only, report_type):
	#REPORT TYPES: "With subtotals based on Source", "with Subtotal for each Form of Payment","Summary based on Referred By"
	data = []

	if totals_only != 1:
		if report_type in ["With subtotals based on Source","Summary based on Referred By"]:
			data = get_all_si(from_date, to_date)
			if report_type == "With subtotals based on Source":
				data = sorted(data, key=lambda k: k['custom_source'], reverse=False)
			else:
				data = sorted(data, key=lambda k: k['custom_practitioner_name'], reverse=False)
		else:
			data = get_all_payments(from_date, to_date)
	
	else:
		data = get_totals_only(from_date, to_date, report_type)
	
	return data

def get_all_si(from_date, to_date):
	data = []

	rows = frappe.db.sql("""SELECT si.* from `tabSales Invoice` si where si.posting_date >=%s and si.posting_date<=%s and 
					  si.docstatus = 1""",(from_date,to_date), as_dict = True)
	for row in rows:
		row['sales_invoice'] = row['name']
		row['payment_modes'] = get_payment_modes(row['name'])
		data.append(row)

	return data

def get_all_payments(from_date, to_date):
	data = []
	rows = frappe.db.sql("""SELECT pmt.payment_mode, pmt.amount, si.* from `tabSales Invoice` si join `tabInvoice Payment Table` pmt 
					  on pmt.parent = si.name where si.posting_date >=%s and si.posting_date<=%s and 
					  si.docstatus = 1""",(from_date,to_date), as_dict = True)
	for row in rows:
		row['sales_invoice'] = row['name']
		data.append(row)

	return data

def get_payment_modes(sales_invoice):
	payment_methods = ""
	rows = frappe.db.sql("""SELECT payment_mode from `tabInvoice Payment Table` where parent = %s""",sales_invoice)
	for i, row in enumerate(rows):
		payment_methods+=str(row[0])
		if len(rows)!= i+1:
			payment_methods+=', '
	
	print(payment_methods)
	print("#####################")
	
	return payment_methods

def get_totals_only(from_date, to_date, report_type):
	data = []
	
	#REPORT TYPES: "With subtotals based on Source", "with Subtotal for each Form of Payment","Summary based on Referred By"
	if report_type == "With subtotals based on Source":
		data = frappe.db.sql("""SELECT custom_source, sum(total) as total, sum(discount_amount) as discount_amount, sum(net_total) 
			   					as net_total from `tabSales Invoice` where posting_date >=%s and posting_date <=%s and docstatus = 1
					   			group by custom_source""",
								(from_date, to_date), as_dict = True)
	elif report_type == "Summary based on Referred By":
		data = frappe.db.sql("""SELECT custom_practitioner_name, sum(total) as total, sum(discount_amount) as discount_amount, sum(net_total) 
								as net_total from `tabSales Invoice` where posting_date >=%s and posting_date <=%s and docstatus = 1
					   			group by custom_practitioner_name""",
						(from_date, to_date), as_dict = True)

	else:
		data = frappe.db.sql("""SELECT pmt.payment_mode as payment_mode, sum(pmt.amount) as amount from `tabInvoice Payment Table` pmt join `tabSales Invoice` si 
					   			on si.name = pmt.parent	where si.posting_date >=%s and si.posting_date <=%s and si.docstatus = 1
					   			group by pmt.payment_mode""",
						(from_date, to_date), as_dict = True)

	return data