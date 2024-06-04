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

# def get_idx(si):
#     current_id = frappe.db.sql("""SELECT MAX(idx) from `tabPF and Incentive Item` where parent = %s""",si)
#     if current_id[0][0] is None:
#         return 1
#     else:
#         return (current_id[0][0]+1)

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

def obrero_fix():
    si_list = frappe.db.sql("""SELECT name, ref_practitioner, custom_practitioner_name from `tabSales Invoice` where ref_practitioner like %s and
                            custom_practitioner_name like %s and docstatus = 1""",('%'+'OBRERO'+'%','%'+'ZAYNAB'+'%'))
    for si in si_list:
        print(si[0], si[1], si[2])
        #HLC-PRAC-2024-00018
        frappe.db.sql("""UPDATE `tabSales Invoice` set ref_practitioner = 'HLC-PRAC-2024-00018' where name = %s""",si[0])
        frappe.db.sql("""UPDATE `tabPF and Incentive Item` set doctor = 'HLC-PRAC-2024-00018' where item_code = 'INCENTIVE' and parent = %s""",si[0])
        frappe.db.commit()
    
    labs_list = frappe.db.sql("""SELECT name, practitioner, practitioner_name from `tabLab Test` where practitioner like %s and
                            practitioner_name like %s and docstatus = 1""",('%'+'OBRERO'+'%','%'+'ZAYNAB'+'%'))
    for lab in labs_list:
        print(lab[0], lab[1], lab[2])
        frappe.db.sql("""UPDATE `tabLab Test` set practitioner = 'HLC-PRAC-2024-00018' where name = %s""",lab[0])
        frappe.db.commit()