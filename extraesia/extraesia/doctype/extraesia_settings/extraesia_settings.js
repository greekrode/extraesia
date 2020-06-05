// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Extraesia Settings', {
	recalculate_items_balance: function(frm) {
		frappe.call({
			method: 'extraesia.item.recalculate_items_balance',
			callback: function(r) {
				if (!r.exc) {
					frappe.msgprint(r.message);
					// console.log(r.message);
				}
			}
		});
	}
});
