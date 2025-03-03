import frappe, datetime, json

def on_save(doc, method):
    lastname = doc.last_name
    firstname = doc.first_name
    middlein = doc.middle_name[0] if (doc.middle_name is not None and doc.middle_name != "") else None
    birthdate = datetime.datetime.strptime(doc.dob,"%Y-%m-%d")
    patient_name = lastname + ", "+ firstname

    if middlein is not None:
        patient_name = patient_name + " " + middlein+ "."
    
    doc.patient_name = patient_name
 
    doc.patient_id = lastname[0]+firstname[0]+str(birthdate.month).zfill(2)+str(birthdate.day).zfill(2)+str(birthdate.year)
    doc.uid = doc.patient_id
    try:
        if doc.__islocal:
            doc.name = doc.patient_id
    except:
        pass

@frappe.whitelist()
def update_patient_details(doc):
    print(doc)
    doc = json.loads(doc)
    old_name = doc['name']
    new_name = doc['uid']
    print(old_name, new_name, "####################")

    if old_name!=new_name:
        print(old_name==new_name)
        print("Patient Exists?", patient_exists(new_name))
        if patient_exists(new_name):
            frappe.throw("There is a patient with the same ID. Please check.")
            return "Update did not complete. Please check if there were errors."
        else:
            print("RENAME")
            frappe.rename_doc(doc['doctype'],old_name, new_name, force=True, show_alert=True)
            frappe.rename_doc('Customer',doc['customer'], doc['patient_name'],  force=True, show_alert=True)  #update customer
            frappe.db.commit()

    try:
        update_sis(new_name, doc['patient_name'])
        update_labs(new_name, doc['patient_name'])
    except:
        return "Updating Transactions did not complete. Please check if there were errors."
    else:
        return "Finished Update."

def patient_exists(patient_uid):
    count_patients = frappe.db.sql("""select count(*) from `tabPatient` where name = %s""", patient_uid)
    if len(count_patients)>0:
        if count_patients[0][0] > 0:
            return True
        else:
            return False
    else:
        return False
    
def update_sis(patient, patient_name):
    sis = frappe.db.sql("""select name from `tabSales Invoice` where patient = %s """, patient)
    for si in sis:
        print(si[0])
        print("update patient name to ", patient_name)
        frappe.db.sql("""UPDATE `tabSales Invoice` set patient_name = %s, customer_name = %s, title=%s where name = %s""", (patient_name, patient_name, patient_name, si[0]))
        frappe.db.commit()


    
def update_labs(patient, patient_name):
    sis = frappe.db.sql("""select name from `tabLab Test` where patient = %s """, patient)
    for si in sis:
        print(si[0])
        print("update patient name to ", patient_name)
        frappe.db.sql("""UPDATE `tabLab Test` set patient_name = %s where name = %s""", (patient_name, patient_name, si[0]))
        frappe.db.commit()