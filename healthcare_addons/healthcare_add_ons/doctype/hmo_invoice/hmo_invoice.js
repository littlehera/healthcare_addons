// Copyright (c) 2025, littlehera and contributors
// For license information, please see license.txt

frappe.ui.form.on('HMO Invoice', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('HMO Invoice Item', 'amount', function(frm,cdt,cdn){
	var total = 0;
	var items = frm.doc.items;
	console.log(items)
	for(var i = 0; i<items.length;i++)
	{
		console.log(items[i].amount);
		total += items[i].amount;
	}
	frm.set_value('grand_total',total);
	frm.set_value('less_vat',(total/1.12))
	frm.set_value('vat_amount', total -(total/1.12) )
});