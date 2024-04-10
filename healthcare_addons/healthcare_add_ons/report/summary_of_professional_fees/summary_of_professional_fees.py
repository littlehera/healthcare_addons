# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	report_type = filters.get("report_type")
	ref_practitioner = filters.get("ref_practitioner") if filters.get("ref_practitioner") is not None else ""
	item_code = filters.get("item_code") if filters.get("item_code") is not None else ""
	sort_key = "doctor"
	show_totals = filters.get("show_totals")
	
	columns =[
		# {"label": "Sales Invoice #", 'width': 150, "fieldname": "parent", "fieldtype":"Link", "options":"Sales Invoice"},
		{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
		{"label": "Patient Name", 'width': 130, "fieldname": "patient_name"},
		{"label": "MD/Reader", 'width': 130, "fieldname": "doctor"},
		{"label": "Lab Test", 'width': 100, "fieldname": "item_code"},
		{"label": "Gross Amount", 'width': 150, "fieldname": "grand_total", "fieldtype":"Currency", "precision":2},
		{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
		{"label": "PF Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2},
		{"label": "Amount to Turnover", 'width': 150, "fieldname": "amount_to_turnover", "fieldtype":"Currency", "precision":2},
	]

	if report_type == 'PF By Lab Test':
		sort_key = 'item_code'
	else:
		sort_key = 'doctor'

	data = get_data(from_date, to_date, report_type, ref_practitioner, item_code)
	data = sorted(data, key=lambda k: k[sort_key], reverse=False)

	for row in data:
		row['posting_date'] = frappe.db.get_value("Sales Invoice",row['parent'],'posting_date')
		row['patient_name'] = frappe.db.get_value("Sales Invoice",row['parent'],'patient_name')
		row['grand_total'], row['net_total'] = get_item_amounts(row['item_code'], row['parent'])
		#row['grand_total'] = frappe.db.get_value("Sales Invoice",row['parent'],'grand_total')
		#row['net_total'] = frappe.db.get_value("Sales Invoice",row['parent'],'net_total')
		row['doctor'] = get_practitioner_name(row['doctor'])

	if not show_totals:
		data = insert_subtotals(data,sort_key)
		data = insert_total_row(data, sort_key)
	else:
		data = get_subtotals(data, sort_key)
		data = insert_total_row(data, sort_key)

	return columns, data

def get_data(from_date, to_date, report_type, ref_practitioner, item_code):
	pf_type = ""
	order_by = ""
	if "Consultation" in report_type:
		pf_type = "MD Consultation PF"
		order_by = "doctor"
	elif "Reading" in report_type:
		pf_type = "Reading PF"
		order_by = "doctor"
	else:
		pf_type= "Reading PF"
		order_by = "item_code"
	return frappe.db.sql("""SELECT parent, item_code, amount, doctor, amount_to_turnover from `tabPF and Incentive Item` 
					   			where docstatus = 1 and pf_type like %s and doctor like %s and item_code like %s and  
					  			parent in (select name from `tabSales Invoice`
					  			where posting_date >=%s and posting_date <=%s) order by %s""",
								('%'+pf_type+'%','%'+ref_practitioner+'%', '%'+item_code+'%',from_date, to_date, order_by), as_dict = True)

def get_practitioner_name(ref_practitioner):
	return frappe.db.get_value("Healthcare Practitioner",ref_practitioner,"practitioner_name")

def get_item_amounts(item_code, parent):
	rates = frappe.db.sql("""SELECT rate, net_rate from `tabSales Invoice Item` where item_code=%s and parent = %s""",(item_code, parent))
	if len(rates)>0:
		return rates[0][0], rates[0][1]
	else:
		return 0,0

def insert_subtotals(data, key_name):
	new_data = []

	grand_total = 0
	net_total = 0
	total_amount = 0
	total_turnover_amount = 0

	prev_key_value = None
	for row in data:
		if (prev_key_value!= row[key_name]) or (prev_key_value is None):
			if (prev_key_value is not None):
				new_data.append({
					key_name:"Total for "+str(prev_key_value), 
					"grand_total": grand_total,
					"net_total": net_total,
					"amount":total_amount,
					"amount_to_turnover":total_turnover_amount})
				grand_total = 0
				net_total = 0
				total_amount = 0
				total_turnover_amount = 0
			prev_key_value = row[key_name]
		
		new_data.append(row)
		grand_total += float(row['grand_total'])
		net_total += float(row['net_total'])
		total_amount += float(row['amount'])
		total_turnover_amount += float(row['amount_to_turnover'])
	
	new_data.append({key_name:"Total for "+str(prev_key_value), "grand_total": grand_total,
					"net_total": net_total, "amount":total_amount, "amount_to_turnover":total_turnover_amount})
	return new_data

def get_subtotals(data, key_name):
	new_data = []

	grand_total = 0
	net_total = 0
	total_amount = 0
	total_turnover_amount = 0

	prev_key_value = None
	for row in data:
		if (prev_key_value!= row[key_name]) or (prev_key_value is None):
			if (prev_key_value is not None):
				new_data.append({
					key_name:str(prev_key_value), 
					"grand_total": grand_total,
					"net_total": net_total,
					"amount":total_amount,
					"amount_to_turnover":total_turnover_amount})
				grand_total = 0
				net_total = 0
				total_amount = 0
				total_turnover_amount = 0
			prev_key_value = row[key_name]
		grand_total += float(row['grand_total'])
		net_total += float(row['net_total'])
		total_amount += float(row['amount'])
		total_turnover_amount += float(row['amount_to_turnover'])
	
	new_data.append({key_name:str(prev_key_value), "grand_total": grand_total,
					"net_total": net_total, "amount":total_amount, "amount_to_turnover":total_turnover_amount})
	return new_data

def insert_total_row(data, key_value):
	amount = 0
	grand_total = 0
	net_total = 0
	total_turnover_amount = 0
	for row in data:
		if 'Total for' in row[key_value]:
			continue
		else:
			grand_total += float(row['grand_total'])
			net_total += float(row['net_total'])
			amount += float(row['amount'])
			total_turnover_amount += float(row['amount_to_turnover'])


	data.append({"doctor":"TOTAL", "amount":amount,"grand_total": grand_total,
					"net_total": net_total, "amount_to_turnover":total_turnover_amount})
	return data