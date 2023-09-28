# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list


def validate_si(doc, method):
    make_packing_list(doc)
    check_employee_benefit(doc)
    validate_payments(doc)
    pull_item_pf_incentives(doc)

def submit_si(doc,method):
    check_doctor_not_blank(doc)

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

    ### FOR SI ITEMS
    for item in doc.items:
        pf_type = "" #Select: Reading PF, Promo Consultation PF, MD Consultation PF, Incentive
        amount = 0
        amount_to_turnover = 0
        if is_package(item.item_code):
            amount = frappe.db.get_value("Product Bundle", item.item_code, "custom_incentive_amount")
            pf_type ="Incentive"
            amount_to_turnover = amount
        elif is_promo(item.item_code):
            amount = frappe.db.get_value("Product Bundle", item.item_code, "custom_md_pf")
            pf_type = "MD Consultation PF"
            amount_to_turnover = amount
            doc.amount_eligible_for_commission -= amount
            doc.total_commission = doc.amount_eligible_for_commission * (doc.commission_rate/100)
        else:
            item_group = frappe.db.get_value("Item", item.item_code, "item_group")
            if item_group == "Laboratory":
                amount = frappe.db.get_value("Item", item.item_code, "custom_professional_fee")
                pf_type = "Reading PF"
                amount_to_turnover = amount
            else:
                pf_type = "MD Consultation PF"
                amount = (item.amount * 0.8) if ("SC/PWD" in doc.custom_source) else item.amount
                amount_to_turnover = amount * 0.88
        if amount > 0:
            doctor = item.custom_doctor
            pf_row = {
                "item_code":item.item_code,
                "amount": amount,
                "doctor": doctor,
                "pf_type": pf_type,
                "amount_to_turnover":amount_to_turnover
                }
            
            if not check_in_pf_items(pf_row,doc.custom_pf_and_incentives, doctor):
                pf_row = doc.append("custom_pf_and_incentives",pf_row)

    ##FOR BUNDLE ITEMS
    if doc.packed_items:
        for item in doc.packed_items:
            amount = frappe.db.get_value("Item", item.item_code, "custom_professional_fee")
            pf_type = "Reading PF"
            amount_to_turnover = amount
            if amount > 0:
                pf_row = {
                    "item_code":item.item_code,
                    "amount": amount,
                    "pf_type": pf_type,
                    "amount_to_turnover":amount
                    }
                if not check_in_pf_items(pf_row,doc.custom_pf_and_incentives):
                    pf_row = doc.append("custom_pf_and_incentives",pf_row)
                    frappe.msgprint("Please enter doctor for PF/Incentive row"+str(pf_row.idx)+" | "+pf_row.item_code)

def is_package(item_code):
    is_pckg = False
    count_package = frappe.db.sql("""SELECT COUNT(*) from `tabProduct Bundle` where custom_type = 'Package' and new_item_code = %s""",item_code)
    if count_package[0][0]>0:
        is_pckg = True
    return is_pckg


def is_promo(item_code):
    is_promo = False
    count_promo = frappe.db.sql("""SELECT COUNT(*) from `tabProduct Bundle` where custom_type = 'Promo' and new_item_code = %s""",item_code)
    if count_promo[0][0]>0:
        is_promo = True
    return is_promo

def check_in_pf_items(row, items, doctor = None):
    is_match = False
    for item in items:
        item_row = {
            "item_code":item.item_code,
            "amount": item.amount,
            "pf_type": item.pf_type,
            "amount_to_turnover":item.amount_to_turnover
        }
        if doctor is not None:
            item_row['doctor'] = doctor
        if row == item_row:
            is_match = True
    return is_match

def check_doctor_not_blank(doc):
    for row in doc.custom_pf_and_incentives:
        if row.doctor is None or row.doctor == "":
            frappe.throw("Enter a valid doctor for PF/INCENTIVE "+row.item_code+"| row # "+str(row.idx))