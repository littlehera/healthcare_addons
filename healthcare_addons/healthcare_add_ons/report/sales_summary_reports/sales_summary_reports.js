// Copyright (c) 2023, littlehera and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Summary Reports"] = {
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
            "fieldname": "report_type",
            "label": __("Report Type"),
            "fieldtype": "Select",
            "options": ["With subtotals based on Source", "with Subtotal for each Form of Payment","Summary based on Referred By"],
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
            "label": __("Referred By"),
            "fieldtype": "Link",
            "options": "Healthcare Practitioner",
            "reqd": 0
        },
        {
            "fieldname": "custom_source",
            "label": __("Source"),
            "fieldtype": "Select",
            "options": ["","Doctor's Referral- Regular","Doctor's Referral- SC/PWD","Walk-in-Regular","Walk-in - SC/PWD","HMO","Company","Package","Promo","Employee Benefit"],
            "reqd": 0
        },
        {
            "fieldname": "payment_mode",
            "label": __("Payment Mode"),
            "fieldtype": "Link",
            "options": "Mode of Payment",
            "reqd": 0
        }
        
	],
    "formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
        if(!(typeof data["custom_source"]=="undefined"))
            if (data["custom_source"].includes('Total for')||data["custom_source"].includes('TOTAL')){
                value = '<b style="background: #ffe9a5;">'+value+'</b>'
        }
        if(!(typeof data["ref_practitioner"]=="undefined"))
            if (data["ref_practitioner"].includes('Total')||data["ref_practitioner"].includes('TOTAL')){
                value = '<b style="background: #ffe9a5;">'+value+'</b>'
            }
        if(!(typeof data["payment_mode"]=="undefined"))
            if (data["payment_mode"].includes('Total')||data["payment_mode"].includes('TOTAL')){
                value = '<b style="background: #ffe9a5;">'+value+'</b>'
            }
        if(!(typeof data["sales_invoice"]=="undefined"))
            if (data["sales_invoice"].includes('Total')||data["sales_invoice"].includes('TOTAL')){
                value = '<b style="background: #ffe9a5;">'+value+'</b>'
            }
		return value
	}
};
