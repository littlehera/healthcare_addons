# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	#filters: from_date, to_date, report_type,referred_by,package

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	report_type = filters.get("report_type")
	referred_by = filters.get("referred_by") if filters.get("referred_by") is not None else ""
	package = filters.get("package") if filters.get("package") is not None else ""

	columns = get_columns(report_type)
	data = get_data(from_date, to_date, report_type, referred_by, package)

	return columns, data

def get_columns(report_type):
	if report_type == "By MD":
		columns =[
			{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
			{"label": "Referring Practitioner #", 'width': 150, "fieldname": "custom_practitioner_name", "fieldtype":"Data"},
			{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
			{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
			{"label": "Discount Amount", 'width': 150, "fieldname": "discount_amount", "fieldtype":"Currency", "precision":2},
			{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
			{"label": "Amount Eligible for Incentive", 'width': 150, "fieldname": "amount_eligible_for_commission", "fieldtype":"Currency", "precision":2},
			{"label": "Incentive Amount", 'width': 150, "fieldname": "total_commission", "fieldtype":"Currency", "precision":2}
		]
	else:
		columns =[
			{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
			{"label": "External Referrer", 'width': 150, "fieldname": "custom_external_referrer", "fieldtype":"Data"},
			{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
			{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
			{"label": "Discount Amount", 'width': 150, "fieldname": "discount_amount", "fieldtype":"Currency", "precision":2},
			{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
			{"label": "Incentive Amount", 'width': 150, "fieldname": "total_commission", "fieldtype":"Currency", "precision":2}
		]
	return columns

def get_data(from_date, to_date, report_type, referred_by = None, package = None):
	data = []

	if report_type == "By MD":
		data = frappe.db.sql("""SELECT name as sales_invoice, posting_date, custom_practitioner_name, total, discount_amount, net_total, 
					   			total_commission, (net_total - total_commission) as net_sales, amount_eligible_for_commission
					   			from `tabSales Invoice` where docstatus = 1 and posting_date >=%s and posting_date <=%s and ref_practitioner like %s
					   			and total_commission > 0""",
								(from_date, to_date, '%'+referred_by+'%'), as_dict = True)
	else:
		if package is None:
			frappe.throw("Please select a Package")
		else:
			data = frappe.db.sql("""SELECT name as sales_invoice, posting_date, custom_external_referrer, total, discount_amount, net_total, 
									total_commission, (net_total - total_commission) as net_sales, amount_eligible_for_commission
									from `tabSales Invoice` where docstatus = 1 and posting_date >=%s and posting_date <=%s and ref_practitioner like %s
									and name in (SELECT parent from `tabSales Invoice Item` where item_code = %s)""",
									(from_date, to_date, '%'+referred_by+'%', package), as_dict = True)
			for row in data:
				row['total_commission'] = float(row['total_commission']) + float(get_incentive_amount(package))
				row['net_sales'] = float(row['net_sales']) - float(get_incentive_amount(package))

	return data

def get_incentive_amount(product_bundle):
	return frappe.db.get_value("Product Bundle", product_bundle, "custom_incentive_amount")



def insert_subtotals(data, key_name):
	new_data = []

	total_amount = 0
	total_turnover_amount = 0

	prev_key_value = None
	for row in data:
		if (prev_key_value!= row[key_name]) or (prev_key_value is None):
			if (prev_key_value is not None):
				new_data.append({key_name:"Total for "+str(prev_key_value), "amount":total_amount,"amount_to_turnover":total_turnover_amount})
				total_amount = 0
				total_turnover_amount = 0
			prev_key_value = row[key_name]
		
		new_data.append(row)
		total_amount += float(row['amount'])
		total_turnover_amount += float(row['amount_to_turnover'])
	
	new_data.append({key_name:"Total for "+str(prev_key_value), "amount":total_amount, "amount_to_turnover":total_turnover_amount})
	return new_data

def insert_total_row(data, key_value):
	amount = 0
	total_turnover_amount = 0
	for row in data:
		if 'Total for' in row[key_value]:
			continue
		else:
			amount += float(row['amount'])
			total_turnover_amount += float(row['amount_to_turnover'])


	data.append({"sales_invoice":"TOTAL", "amount":amount,"amount_to_turnover":total_turnover_amount})
	return data