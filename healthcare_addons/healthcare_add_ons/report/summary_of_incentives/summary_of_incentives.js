// Copyright (c) 2023, littlehera and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Summary of Incentives"] = {
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
            "options": ['By MD','By Package'],
            "reqd": 1
		},
        {
            "fieldname": "referred_by",
            "label": __("Referring Practitioner"),
            "fieldtype": "Link",
            "options": "Healthcare Practitioner",
            "reqd": 0

        },
		{
            "fieldname": "package",
            "label": __("Package"),
            "fieldtype": "Link",
            "options": "Product Bundle",
            "reqd": 0,
			"get_query": function(){
				return{
					"filters":{'custom_type':'Package'}
        		}
    		}

        }

	]
};
