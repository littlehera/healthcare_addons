# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list


def validate_si(doc, method):
    make_packing_list(doc)
    check_employee_benefit(doc)
    validate_payments(doc)
    pull_item_pf_incentives(doc)
    check_hmo_card_no(doc)
    check_or(doc)

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
    less_pfs = 0

    ### FOR SI ITEMS
    for item in doc.items:
        utz = is_utz(item.item_code)
        doctor = None
        pf_type = "" #Select: Reading PF, Promo Consultation PF, MD Consultation PF, Incentive
        amount = 0
        amount_to_turnover = 0
        if is_package(item.item_code):
            bundle_name = frappe.db.get_value("Product Bundle", {'new_item_code':item.item_code}, "name")
            amount = frappe.db.get_value("Product Bundle", bundle_name, "custom_incentive_amount")
            pf_type ="Incentive"
            amount_to_turnover = amount
            less_pfs += item.amount

        elif is_promo(item.item_code):
            bundle_name = frappe.db.get_value("Product Bundle", {'new_item_code':item.item_code}, "name")
            amount = frappe.db.get_value("Product Bundle", bundle_name, "custom_md_pf")
            pf_type = "MD Consultation PF"
            amount_to_turnover = amount
            doc.amount_eligible_for_commission = doc.grand_total
            doc.amount_eligible_for_commission -= amount
            doc.total_commission = doc.amount_eligible_for_commission * (doc.commission_rate/100)
            #less_pfs += item.amount

        else:
            item_group = frappe.db.get_value("Item", item.item_code, "item_group")
            if item_group == "Laboratory":
                pf_perc = frappe.db.get_value("Item", item.item_code, "custom_professional_fee_percentage")
                # print(item.item_code,pf_perc,"###################")
                if utz:
                    doctor = item.custom_doctor
                    amount = (pf_perc/100)*item.amount
                    amount = (amount * 0.8) if ("SC/PWD" in doc.custom_source) else amount
                    pf_type = "Reading PF"
                    amount_to_turnover = amount
                    print(amount_to_turnover,"AMOUNT TO TURNOVER")
                else:
                    if pf_perc > 0:
                        # print("PF PERC")
                        doctor = item.custom_doctor
                        amount = (pf_perc/100)*item.amount
                        amount = (amount * 0.8) if ("SC/PWD" in doc.custom_source) else amount
                        pf_type = "Reading PF"
                        amount_to_turnover = amount
                        print(amount_to_turnover,"AMOUNT TO TURNOVER")
                    else:
                        doctor = item.custom_doctor
                        amount = frappe.db.get_value("Item", item.item_code, "custom_professional_fee")
                        amount = (amount * 0.8) if ("SC/PWD" in doc.custom_source) else amount
                        pf_type = "Reading PF"
                        amount_to_turnover = amount
            else:
                if "consultation" in str(item.item_code).lower():
                    doctor = item.custom_doctor
                    pf_type = "MD Consultation PF"
                    amount = (item.amount * 0.8) if ("SC/PWD" in doc.custom_source) else item.amount
                    amount_to_turnover = amount

        if amount > 0 and not utz:
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

        if amount >= 0 and utz:
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
            
            pf_perc = frappe.db.get_value("Item", item.item_code, "custom_professional_fee_percentage")
            pf_fixed = frappe.db.get_value("Item", item.item_code, "custom_professional_fee")
            
            if pf_perc > 0:
                # print("PF PERC")
                # Get item price for the package item where price list = si price list.                
                rate = get_item_price(item.item_code,doc.selling_price_list)
                amount = (pf_perc/100)*rate
                amount = (amount * 0.8) if ("SC/PWD" in doc.custom_source) else amount
                pf_type = "Reading PF"
            
            elif pf_fixed >0:
                amount = pf_fixed
                amount = (amount * 0.8) if ("SC/PWD" in doc.custom_source) else amount
                pf_type = "Reading PF"

            else:
                amount = 0
                
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
    if doc.custom_source in ["Doctor's Referral- MD","Doctor's Referral- Regular","Doctor's Referral- SC/PWD", "Promo", "HMO"]:
        if check_if_consultation(doc):
            pass
        else:
            doc.amount_eligible_for_commission -= less_pfs
            doc.total_commission = doc.amount_eligible_for_commission * (doc.commission_rate/100)
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

    if "Package" in doc.custom_source:
        total_reg_labs = get_total_of_regular_labs(doc.items)
        amount = total_reg_labs * 0.05
        pf_type = "Incentive"
        item_code = "REFERRAL"
        #amount_to_turnover = amount

        if "SC/PWD" in doc.custom_source:
            amount = amount * 0.8
        
        amount_to_turnover = amount

        if amount > 0:
            total_pfs += amount
            pf_row = {
                "item_code":item_code,
                "amount": amount,
                #"external_referrer": doc.custom_external_referrer,
                "pf_type": pf_type,
                "amount_to_turnover":amount_to_turnover
                }
            
            if not check_in_pf_items(pf_row,doc.custom_pf_and_incentives, doctor = None):
                pf_row = doc.append("custom_pf_and_incentives",pf_row)

    doc.custom_net_sales = doc.grand_total - total_pfs

def get_item_price(item_code, price_list):
    item_price = frappe.db.sql("""SELECT price_list_rate from `tabItem Price` where item_code = %s and price_list = %s""",(item_code, price_list))
    if len(item_price)>0:
        return item_price[0][0] if item_price[0][0] is not None else 0
    else:
        return 0

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

def is_utz(item_code):
    is_utz = False
    count_lab_test = frappe.db.sql("""SELECT COUNT(*) from `tabLab Test Template` where item = %s""",(item_code))
    if count_lab_test[0][0]>0:
        is_utz = True
    return is_utz

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
            frappe.throw("Enter a valid doctor/referrer/radiologist for PF/INCENTIVE "+row.item_code+"| row # "+str(row.idx))
        
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


def check_hmo_card_no(doc):
    has_card_no = False
    if "HMO" in doc.custom_source:
        for row in doc.custom_invoice_payments:
            if row.payment_mode == "Charge to HMO" and row.card_no is not None and row.card_no != "":
                print("CARD NO #########################")
                print(row.card_no)
                has_card_no = True

        if has_card_no == False:
            frappe.throw("HMO Card No. is blank. Please place NONE or enter card number.")

def get_total_of_regular_labs(items):
    total_reg_labs = 0
    for item in items:
        if is_package(item.item_code):
            continue
        elif is_promo(item.item_code):
            continue
        else:
            total_reg_labs += item.amount
    return total_reg_labs

def check_or(doc):
    for payment in doc.custom_invoice_payments:
        print(payment.payment_mode, payment.ref_no, doc.name)
        if payment.payment_mode in ["Cash","Credit Card", "GCash", "Charge to Company"]:
            if get_or_match(payment.ref_no, doc.name)>0:
                frappe.throw("REF NO/OR NO Already Exists!")

def get_or_match(or_no, si):
    count_or = frappe.db.sql("""SELECT COUNT(*) from `tabInvoice Payment Table` where ref_no = %s and parent != %s""",(or_no, si))
    if len(count_or)>0:
        return count_or[0][0]
    else:
        return 0

def check_if_consultation(si):
    items = si.items
    if len(items) == 1:
        item_code = items[0].item_code
        print(item_code)
        if "consultation" in str(item_code).lower():
            return True
        else:
            return False
    else:
        return False