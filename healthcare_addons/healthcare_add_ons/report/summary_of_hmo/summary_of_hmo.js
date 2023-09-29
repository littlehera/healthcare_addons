// Copyright (c) 2023, littlehera and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Summary of HMO"] = {
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
            "options": ['Laboratory Tests','Consultation PFs'],
            "reqd": 1
		},
        {
            "fieldname": "hmo",
            "label": __("HMO"),
            "fieldtype": "Link",
            "options": "HMO",
            "reqd": 0

        }
	]
};
