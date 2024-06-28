import frappe, uuid
# from healthcare_addons.public.python.sievents import cancel_si, pull_item_pf_incentives

# def fix_si():
#     si_list = frappe.db.sql("""select itm.item_code, itm.parent, test.patient_name, test.custom_radiologist from 
#                             `tabSales Invoice Item` itm left join `tabLab Test` test on test.custom_sales_invoice = itm.parent
#                             where itm.item_code like '%UTZ%' and itm.docstatus = 1 and itm.parent not in
#                             (select parent from `tabPF and Incentive Item` where item_code like '%UTZ%')""", as_dict = True)
    
#     for si in si_list:
#         name = uuid.uuid4().hex
#         pf_type = "Reading PF"
#         item_code = si.item_code
#         parent = si.parent
#         parentfield = "custom_pf_and_incentives"
#         parenttype = "Sales Invoice"
#         doctor = si.custom_radiologist
#         idx =  get_idx(parent)
#         amount = get_incentive_amount(item_code, parent)
#         if doctor is not None:
#             print("INSERT:", item_code, parent, doctor, idx, amount, name)
#             frappe.db.sql("""INSERT INTO `tabPF and Incentive Item`(name,creation,modified,modified_by,owner,docstatus,idx,item_code,amount,pf_type,
#                           doctor,external_referrer,amount_to_turnover,parent,parentfield,parenttype) VALUES(%s,NOW(),NOW(),'Administrator','Administrator',1,
#                           %s,%s,%s,%s,%s,NULL,%s,%s,%s,%s)""",(name,idx,item_code, amount, pf_type, doctor,amount, parent, parentfield, parenttype))
#             frappe.db.commit()        

def get_idx(si):
    current_id = frappe.db.sql("""SELECT MAX(idx) from `tabPF and Incentive Item` where parent = %s""",si)
    if current_id[0][0] is None:
        return 1
    else:
        return (current_id[0][0]+1)

# def get_incentive_amount(item_code,si):
#     doc = frappe.get_doc("Sales Invoice", si)
#     amount = 0
#     item_group = frappe.db.get_value("Item", item_code, "item_group")
#     if item_group == "Laboratory":
#         pf_perc = frappe.db.get_value("Item", item_code, "custom_professional_fee_percentage")
#         # print(item.item_code,pf_perc,"###################")
#         if pf_perc > 0:
#             # print("PF PERC")
#             amount = (pf_perc/100)*get_item_price(item_code, doc.selling_price_list)
#             amount = (amount * 0.8) if ("SC/PWD" in doc.custom_source) else amount
#         else:
#             amount = frappe.db.get_value("Item", item_code, "custom_professional_fee")
#             amount = (amount * 0.8) if ("SC/PWD" in doc.custom_source) else amount
#     return amount        

# def get_item_price(item_code, price_list):
#     item_price = frappe.db.sql("""SELECT price_list_rate from `tabItem Price` where item_code = %s and price_list = %s""",(item_code, price_list))
#     if len(item_price)>0:
#         return item_price[0][0] if item_price[0][0] is not None else 0
#     else:
#         return 0

def referral_with_hmo():
    sis = frappe.db.sql("""SELECT name, custom_source, custom_hmo, ref_practitioner, net_total from `tabSales Invoice` where custom_source = 'HMO' and posting_date >='2024-06-01'
                            and docstatus =1""")
    for row in sis:
        print(row[0], row[1], row[2], row[3], row[4])

        amount= float(row[4]) * 0.05
        name = uuid.uuid4().hex
        parent = row[0]
        doctor = row[3]
        pf_type = "Incentive"
        item_code = "INCENTIVE"
        parentfield = "custom_pf_and_incentives"
        parenttype = "Sales Invoice"
        idx =  get_idx(parent)
        sales_partner = get_sales_partner(doctor)

        is_consultation, amount_to_deduct = check_if_consultation(parent)
        if is_consultation:
            amount -=amount_to_deduct
        
        if amount > 0:

            frappe.db.sql("""UPDATE `tabSales Invoice` set sales_partner =%s, amount_eligible_for_commission = net_total,
                            commission_rate = 5, total_commission = (net_total * 0.05) where name = %s""",(sales_partner, parent))

            if count_incentive_item(parent,doctor) == 0:
                print("INSERT:", item_code, parent, doctor, idx, amount, name)
                frappe.db.sql("""INSERT INTO `tabPF and Incentive Item`(name,creation,modified,modified_by,owner,docstatus,idx,item_code,amount,pf_type,
                                doctor,external_referrer,amount_to_turnover,parent,parentfield,parenttype) VALUES(%s,NOW(),NOW(),'Administrator','Administrator',1,
                                %s,%s,%s,%s,%s,NULL,%s,%s,%s,%s)""",(name,idx,item_code, amount, pf_type, doctor,amount, parent, parentfield, parenttype))
            frappe.db.commit()

def get_sales_partner(doctor):
    return frappe.db.get_value("Healthcare Practitioner",doctor,"custom_sales_partner")

def count_incentive_item(parent, doctor):
    return frappe.db.sql("""SELECT COUNT(*) from `tabPF and Incentive Item` where parent = %s and item_code = 'INCENTIVE' and doctor = %s""",
                         (parent, doctor))[0][0]

def check_if_consultation(si):
    is_consultation = False
    amount_to_deduct = 0

    si_doc = frappe.get_doc("Sales Invoice", si)

    items = si_doc.items
    for item in items:
        if "CONSULTATION" in str(item.item_code).upper():
            is_consultation = True
            amount_to_deduct += ((item.amount*.8) if "SC/PWD" in si_doc.custom_source else item.amount)
    
    return is_consultation, amount_to_deduct