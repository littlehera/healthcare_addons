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
	data = get_data(from_date, to_date, totals_only, report_type, filters)
	return columns, data

def get_columns(totals_only, report_type):
	#REPORT TYPES: "With subtotals based on Source", "with Subtotal for each Form of Payment","Summary based on Referred By"
	if totals_only != 1:
		if report_type in ["With subtotals based on Source", "Summary based on Referred By"]:
			columns = [
				{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
				{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
				{"label": "Source", 'width': 150, "fieldname": "custom_source"},
				{"label": "HMO", 'width': 150, "fieldname": "custom_hmo"},
				{"label": "Referred By", 'width': 150, "fieldname": "custom_practitioner_name"},
				{"label": "External Referrer", 'width': 150, "fieldname": "custom_external_referrer"},
				{"label": "Patient Name", 'width': 150, "fieldname": "patient_name"},
				{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
				{"label": "Discount %", 'width': 150, "fieldname": "additional_discount_percentage"},
				{"label": "Discount Amount", 'width': 150, "fieldname": "discount_amount", "fieldtype":"Currency", "precision":2},
				{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
				{"label": "Form of Payment", 'width': 150, "fieldname": "payment_modes"},
				{"label": "Ref#/OR#", 'width': 150, "fieldname": "ref_no"}
			]
		else:
			columns = [
				{"label": "Form of Payment", 'width': 150, "fieldname": "payment_mode"},
				{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
				{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
				{"label": "Patient Name", 'width': 150, "fieldname": "patient_name"},
				{"label": "Source", 'width': 150, "fieldname": "custom_source"},
				{"label": "Referred By", 'width': 150, "fieldname": "custom_practitioner_name"},
				{"label": "External Referrer", 'width': 150, "fieldname": "custom_external_referrer"},
				{"label": "Payment Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2},
				{"label": "Ref#/OR#", 'width': 150, "fieldname": "ref_no"}
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

def get_data(from_date, to_date, totals_only, report_type, filters):
	#REPORT TYPES: "With subtotals based on Source", "with Subtotal for each Form of Payment","Summary based on Referred By"
	data = []
	key_value = ""
	if totals_only != 1:
		if report_type in ["With subtotals based on Source","Summary based on Referred By"]:
			data = get_all_si(from_date, to_date, filters)
			if report_type == "With subtotals based on Source":
				key_value = 'custom_source'
			else:
				key_value = 'custom_practitioner_name'

		else:
			key_value = 'payment_mode'
			data = get_all_payments(from_date, to_date, filters)

		data = sorted(data, key=lambda k: k[key_value], reverse=False)
		data = insert_subtotals(data, key_value)
	else:
		key_value = 'payment_mode' if report_type not in ["With subtotals based on Source","Summary based on Referred By"] else ''
		data = get_totals_only(from_date, to_date, report_type, filters)
	
	data = insert_total_row(data, key_value, totals_only)
	
	return data

def get_all_si(from_date, to_date, filters):
	ref_practitioner = filters.get("referred_by") if filters.get("referred_by") is not None else ''
	custom_source = filters.get("custom_source") if filters.get("custom_source") is not None else ''
	payment_mode = filters.get("payment_mode") if filters.get("payment_mode") is not None else ''
	data = []

	query = "SELECT DISTINCT si.* from `tabSales Invoice` si join `tabInvoice Payment Table` pmt on pmt.parent = si.name where si.posting_date >={} and si.posting_date<={} and si.docstatus = 1".format("'"+str(from_date)+"'", "'"+str(to_date)+"'")

	if ref_practitioner != "":
		query += " AND si.ref_practitioner = {}".format("'"+ref_practitioner+"'")
	if custom_source != "":
		query += " AND si.custom_source = {}".format("'"+custom_source+"'")
	if payment_mode != "":
		query += " AND pmt.payment_mode ={}".format("'"+payment_mode+"'")
	
	query += " order by si.name asc, posting_date asc"

	print(query)

	rows = frappe.db.sql(query, as_dict = True)

	# rows = frappe.db.sql("""SELECT DISTINCT si.* from `tabSales Invoice` si join `tabInvoice Payment Table` pmt on pmt.parent = si.name 
	# 				  where si.posting_date >=%s and si.posting_date<=%s and si.docstatus = 1 and si.ref_practitioner like %s
	# 				  and si.custom_source like %s and pmt.payment_mode like %s order by si.name asc, posting_date asc""",
	# 				  (from_date,to_date,'%'+ref_practitioner+'%','%'+custom_source+'%','%'+payment_mode+'%'), as_dict = True)
	for row in rows:
		row['sales_invoice'] = row['name']
		row['payment_modes'] = get_payment_modes(row['name'])
		row['ref_no'] = get_ref_nos(row['name'])
		data.append(row)

	return data

def get_all_payments(from_date, to_date, filters):
	ref_practitioner = filters.get("referred_by") if filters.get("referred_by") is not None else ''
	custom_source = filters.get("custom_source") if filters.get("custom_source") is not None else ''
	payment_mode = filters.get("payment_mode") if filters.get("payment_mode") is not None else ''
	data = []

	query = "SELECT pmt.payment_mode, pmt.amount, pmt.ref_no, si.* from `tabSales Invoice` si join `tabInvoice Payment Table` pmt on pmt.parent = si.name where si.posting_date >={} and si.posting_date<={} and si.docstatus = 1".format("'"+str(from_date)+"'", "'"+str(to_date)+"'")

	if ref_practitioner != "":
		query += " AND si.ref_practitioner = {}".format("'"+ref_practitioner+"'")
	if custom_source != "":
		query += " AND si.custom_source = {}".format("'"+custom_source+"'")
	if payment_mode != "":
		query += " AND pmt.payment_mode ={}".format("'"+payment_mode+"'")

	rows = frappe.db.sql(query, as_dict = True)
	
	# rows = frappe.db.sql("""SELECT pmt.payment_mode, pmt.amount, pmt.ref_no, si.* from `tabSales Invoice` si join `tabInvoice Payment Table` pmt 
	# 			  on pmt.parent = si.name where si.posting_date >=%s and si.posting_date<=%s and 
	# 			  si.docstatus = 1 and si.ref_practitioner like %s and si.custom_source like %s and pmt.payment_mode like %s""",
	# 			  (from_date,to_date,'%'+ref_practitioner+'%','%'+custom_source+'%','%'+payment_mode+'%'), as_dict = True)


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

def get_ref_nos(sales_invoice):
	ref_nos = ""
	rows = frappe.db.sql("""SELECT ref_no from `tabInvoice Payment Table` where parent = %s""",sales_invoice)
	for i, row in enumerate(rows):
		ref_nos+=str(row[0])
		if len(rows)!= i+1:
			ref_nos+=', '
	
	return ref_nos

def get_totals_only(from_date, to_date, report_type, filters):
	ref_practitioner = filters.get("referred_by") if filters.get("referred_by") is not None else ''
	custom_source = filters.get("custom_source") if filters.get("custom_source") is not None else ''
	payment_mode = filters.get("payment_mode") if filters.get("payment_mode") is not None else ''

	data = []
	
	#TODO: If filters are blank, fetch all. if not, use filter and add filter to query

	#REPORT TYPES: "With subtotals based on Source", "with Subtotal for each Form of Payment","Summary based on Referred By"
	if report_type == "With subtotals based on Source":
		data = frappe.db.sql("""SELECT si.custom_source, sum(si.total) as total, sum(si.discount_amount) as discount_amount, sum(si.net_total) 
			   					as net_total from `tabSales Invoice` si where si.posting_date >=%s and si.posting_date<=%s and 
					  			si.docstatus = 1 and si.ref_practitioner like %s and si.custom_source like %s and name in (SELECT parent from 
					   			`tabInvoice Payment Table` pmt where pmt.payment_mode like %s)
					   			group by si.custom_source""",
					  			(from_date,to_date,'%'+ref_practitioner+'%','%'+custom_source+'%','%'+payment_mode+'%'), as_dict = True)
	elif report_type == "Summary based on Referred By":
		data = frappe.db.sql("""SELECT si.custom_practitioner_name, sum(si.total) as total, sum(si.discount_amount) as discount_amount, sum(si.net_total) 
								as net_total from `tabSales Invoice` si where si.posting_date >=%s and si.posting_date<=%s and 
					  			si.docstatus = 1 and si.ref_practitioner like %s and si.custom_source like %s and name in 
					   			(SELECT parent from `tabInvoice Payment Table` pmt where pmt.payment_mode like %s)
					   			group by si.custom_practitioner_name""",
								(from_date,to_date,'%'+ref_practitioner+'%','%'+custom_source+'%','%'+payment_mode+'%'), as_dict = True)

	else:
		data = frappe.db.sql("""SELECT pmt.payment_mode as payment_mode, sum(pmt.amount) as amount from `tabInvoice Payment Table` pmt join `tabSales Invoice` si 
					   			on si.name = pmt.parent	where si.posting_date >=%s and si.posting_date <=%s and si.docstatus = 1 and 
					   			si.ref_practitioner like %s and si.custom_source like %s and pmt.payment_mode like %s
					   			group by pmt.payment_mode""",
								(from_date,to_date,'%'+ref_practitioner+'%','%'+custom_source+'%','%'+payment_mode+'%'), as_dict = True)

	return data

def insert_subtotals(data, key_name):
	new_data = []

	discount_total = 0
	gross_total = 0
	net_total = 0
	total_amount = 0

	prev_key_value = None
	for row in data:
		if (prev_key_value!= row[key_name]) or (prev_key_value is None):
			if (prev_key_value is not None):
				new_data.append({key_name:"Total for "+str(prev_key_value), "discount_amount":discount_total, "amount":total_amount, "total":gross_total, "net_total":net_total})
				discount_total = 0
				gross_total = 0
				net_total = 0
				total_amount = 0
			prev_key_value = row[key_name]
		
		new_data.append(row)

		discount_total += float(row['discount_amount'])
		gross_total += float(row['total'])
		net_total += float(row['net_total'])

		if key_name == 'payment_mode':
			total_amount += float(row['amount'])
	
	new_data.append({key_name:"Total for "+str(prev_key_value), "additional_discount_percentage":None, "discount_amount":discount_total, "total":gross_total, 
					"net_total":net_total, "amount":total_amount})
	return new_data


def insert_total_row(data, key_value, totals_only):
	discount_total = 0
	gross_total = 0
	net_total = 0
	amount = 0 
	for row in data:
		if (totals_only !=1) and 'Total for' in row[key_value]:
			continue
		else:
			if key_value == 'payment_mode':
				amount += float(row['amount'])
			else:
				gross_total += float(row['total'])
				net_total += float(row['net_total'])
				discount_total += float(row['discount_amount'])

	data.append({"sales_invoice":"TOTAL", "custom_source":"TOTAL", "ref_practitioner":"TOTAL", "payment_mode":"TOTAL","additional_discount_percentage":None, "discount_amount":discount_total, "amount":amount, "total":gross_total, "net_total":net_total})
	return data