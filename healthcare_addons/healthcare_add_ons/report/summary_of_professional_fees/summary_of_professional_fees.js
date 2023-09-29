// Copyright (c) 2023, littlehera and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Summary of Professional Fees"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
		{
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
		{
			"fieldname":"report_type",
			"label": __("Report Type"),
			"fieldtype": "Select",
            "options": ['MD Consultation PF','Reading PF'],
            "reqd": 1
		},
		{
            "fieldname": "ref_practitioner",
            "label": __("Doctor"),
            "fieldtype": "Link",
            "options": "Healthcare Practitioner",
            "reqd": 0
        }
	]
};
