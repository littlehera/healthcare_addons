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
    create_pe(doc)
    doc.reload()

def cancel_si(doc,method):
    pes = frappe.db.sql("""SELECT parent from `tabPayment Entry Reference` where reference_name=%s""",doc.name)
    #get all PE's linked to this transaction and cancel PEs.
    for pe in pes:
        frappe.db.sql("""UPDATE `tabPayment Entry` set docstatus = 2, status = 'Cancelled' where name = %s""", pe[0])
        frappe.db.commit()
    
    incentives = frappe.db.sql("""SELECT name from `tabPF and Incentive Item` where parent = %s""",doc.name)
    for incentive in incentives:
        frappe.db.sql("""DELETE from `tabPF and Incentive Item` where name = %s""", incentive[0])
        frappe.db.commit()



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
    total_pfs = 0

    ### FOR SI ITEMS
    for item in doc.items:
        doctor = None
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
            doc.amount_eligible_for_commission = doc.grand_total
            doc.amount_eligible_for_commission -= amount
            doc.total_commission = doc.amount_eligible_for_commission * (doc.commission_rate/100)
        else:
            item_group = frappe.db.get_value("Item", item.item_code, "item_group")
            if item_group == "Laboratory":
                doctor = item.custom_doctor
                amount = frappe.db.get_value("Item", item.item_code, "custom_professional_fee")
                amount = (amount * 0.8) if ("SC/PWD" in doc.custom_source) else amount
                pf_type = "Reading PF"
                amount_to_turnover = amount
            else:
                doctor = item.custom_doctor
                pf_type = "MD Consultation PF"
                amount = (item.amount * 0.8) if ("SC/PWD" in doc.custom_source) else item.amount
                amount_to_turnover = amount * 0.88
        if amount > 0:
            total_pfs += amount
            if doctor is not None:
                pf_row = {
                    "item_code":item.item_code,
                    "amount": amount,
                    "doctor": doctor,
                    "pf_type": pf_type,
                    "amount_to_turnover":amount_to_turnover
                    } 
                if not check_in_pf_items(pf_row,doc.custom_pf_and_incentives, doctor):
                    pf_row = doc.append("custom_pf_and_incentives",pf_row)
            else:
                pf_row = {
                    "item_code":item.item_code,
                    "amount": amount,
                    "pf_type": pf_type,
                    "amount_to_turnover":amount_to_turnover
                    } 
                if not check_in_pf_items(pf_row,doc.custom_pf_and_incentives):
                    pf_row = doc.append("custom_pf_and_incentives",pf_row)
    ##FOR BUNDLE ITEMS
    if doc.packed_items:
        for item in doc.packed_items:
            amount = frappe.db.get_value("Item", item.item_code, "custom_professional_fee")
            pf_type = "Reading PF"
            amount_to_turnover = amount
            if amount > 0:
                total_pfs += amount
                pf_row = {
                    "item_code":item.item_code,
                    "amount": amount,
                    "pf_type": pf_type,
                    "amount_to_turnover":amount
                    }
                if not check_in_pf_items(pf_row,doc.custom_pf_and_incentives):
                    pf_row = doc.append("custom_pf_and_incentives",pf_row)
                    frappe.msgprint("Please enter doctor for PF/Incentive row"+str(pf_row.idx)+" | "+pf_row.item_code)
    
       ### For Sales Partner/Health Practitioner Incentives
    if doc.custom_source in ["Doctor's Referral- MD","Doctor's Referral- Regular","Doctor's Referral- SC/PWD", "Promo"]:
        amount = doc.total_commission
        pf_type = "Incentive"
        item_code = "INCENTIVE"
        doctor = doc.ref_practitioner
        amount_to_turnover = amount

        if amount > 0:
            total_pfs += amount
            pf_row = {
                "item_code":item_code,
                "amount": amount,
                "doctor": doctor,
                "pf_type": pf_type,
                "amount_to_turnover":amount_to_turnover
                }
            
            if not check_in_pf_items(pf_row,doc.custom_pf_and_incentives, doctor):
                pf_row = doc.append("custom_pf_and_incentives",pf_row)

    doc.custom_net_sales = doc.grand_total - total_pfs

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
        if (row.doctor is None or row.doctor == "") and (row.external_referrer is None or row.external_referrer == ""):
            frappe.throw("Enter a valid doctor for PF/INCENTIVE "+row.item_code+"| row # "+str(row.idx))
        
def create_pe(doc):
    reference_date = doc.posting_date
    payment_type = "Receive"
    party_type = "Customer"
    party = doc.customer
    party_name = doc.customer_name
    paid_to = "1110 - Cash - PL"
    doctype = "Payment Entry"

    for row in doc.custom_invoice_payments:
        paid_amount = row.amount
        reference_no = row.ref_no
        mode_of_payment = row.payment_mode

        pe_dict = {
            "doctype":doctype,
            "reference_date":reference_date,
            "posting_date":reference_date,
            "payment_type":payment_type,
            "party_type":party_type,
            "party":party,
            "party_name":party_name,
            "paid_to":paid_to,
            "paid_amount":paid_amount,
            "received_amount":paid_amount,
            "reference_no": reference_no,
            "mode_of_payment":mode_of_payment
        }

        pe_doc = frappe.get_doc(pe_dict)

        pe_ref = {
            "reference_doctype":"Sales Invoice",
            "reference_name": doc.name,
            "allocated_amount": paid_amount
                }
        
        pe_doc.append("references",pe_ref)

        pe_doc.insert()
        pe_doc.submit()
