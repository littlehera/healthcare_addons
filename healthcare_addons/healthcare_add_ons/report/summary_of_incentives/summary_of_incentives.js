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
            "fieldname": "totals_only",
            "label": __("Show Totals Only?"),
            "fieldtype": "Check",
            "default":0
        },
        {
            "fieldname": "referred_by",
            "label": __("Requesting Physician"),
            "fieldtype": "Link",
            "options": "Healthcare Practitioner",
            "reqd": 0

        },
        {
            "fieldname": "external_referrer",
            "label": __("External Referrer"),
            "fieldtype": "Link",
            "options": "External Referrer",
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

	],
    "formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
        if(!(typeof data["custom_practitioner_name"]=="undefined"))
             if (data["custom_practitioner_name"].includes('Total')||data["custom_practitioner_name"].includes('TOTAL')){
                value = '<b style="background: #ffe9a5;">'+value+'</b>'
             }
        if(!(typeof data["sales_invoice"]=="undefined"))
             if (data["sales_invoice"].includes('Total')||data["sales_invoice"].includes('TOTAL')){
                value = '<b style="background: #ffe9a5;">'+value+'</b>'
             }
        if(!(typeof data["custom_external_referrer"]=="undefined"))
             if (data["custom_external_referrer"].includes('Total')||data["custom_external_referrer"].includes('TOTAL')){
                value = '<b style="background: #ffe9a5;">'+value+'</b>'
             }
		return value
	}
};
