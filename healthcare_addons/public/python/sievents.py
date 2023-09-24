# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list


def validate_si(doc, method):
    make_packing_list(doc)
    check_employee_benefit(doc)
    validate_payments(doc)
    pull_item_pf_incentives(doc)

def check_employee_benefit(doc):
    has_employee_benefit = 0
    payments = doc.custom_invoice_payments
    for payment in payments:
        if payment.payment_mode =="Employee Benefit":
            has_employee_benefit = 1
    
    if (has_employee_benefit == 1) and ((doc.custom_employee=="") or (doc.custom_employee==None)):
        frappe.throw("Employee Cannot be Blank. Please specify employee.")


def validate_payments(doc):
    total = 0
    payments = doc.custom_invoice_payments
    for payment in payments:
        total += payment.amount
    
    if total != doc.net_total:
        frappe.throw("TOTAL PAYMENTS DOES NOT MATCH INVOICE NET TOTAL AMOUNT!")

def pull_item_pf_incentives(doc):
    for item in doc.items:
        item.custom_lab_pf = frappe.db.get_value("Item", item.item_code, "custom_professional_fee")
        if is_package(item.item_code):
            item.custom_incentive_amount = frappe.db.get_value("Product Bundle", item.item_code, "custom_incentive_amount")
        else:
            item.custom_incentive_amount = 0

def is_package(item_code):
    is_pckg = False
    count_package = frappe.db.sql("""SELECT COUNT(*) from `tabProduct Bundle` where custom_type = 'Package' and new_item_code = %s""",item_code)
    if count_package[0][0]>0:
        is_pckg = True
    return is_pckg