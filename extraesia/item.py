from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.utils import get_stock_balance, get_latest_stock_qty
from erpnext.stock.dashboard.item_dashboard import get_data


def set_item_balance(doc,method):
    balance = get_item_balance(doc.item_code) or 0
    if not doc.actual_qty :
        diff = balance - doc.qty_after_transaction
        frappe.db.set_value("Item",doc.item_code,"balance",doc.qty_after_transaction)
        frappe.db.set_value("Item",doc.item_code,"available_qty",get_item_available_qty(doc.item_code) - diff)
    else:
        balance +=  doc.actual_qty
        frappe.db.set_value("Item",doc.item_code,"balance",balance)
        if doc.actual_qty > 0 and doc.voucher_type == "Stock Entry":
            stock_entry_type = frappe.db.get_value("Stock Entry",doc.voucher_no,"stock_entry_type")
            work_order = frappe.db.get_value("Stock Entry",doc.voucher_no,"work_order")
            if stock_entry_type == "Manufacture" and work_order:
                frappe.db.set_value("Item",doc.item_code,"available_qty",get_item_available_qty(doc.item_code))
            else:
                frappe.db.set_value("Item",doc.item_code,"available_qty",get_item_available_qty(doc.item_code) + doc.actual_qty)
        else:
            frappe.db.set_value("Item",doc.item_code,"available_qty",get_item_available_qty(doc.item_code) + doc.actual_qty)


def set_item_balance_on_delete(doc,method):
    balance = get_item_balance(doc.item_code) or 0
    balance += doc.actual_qty
    frappe.db.set_value("Item",doc.item_code,"balance",balance)
    frappe.db.set_value("Item",doc.item_code,"available_qty",get_item_available_qty(doc.item_code) - doc.actual_qty)


def set_item_balance_after_delete_stock_reconciliation(doc,method):
    for item in doc.items:    
        balance = get_item_balance(item.item_code) or 0
        frappe.db.set_value("Item",item.item_code,"balance",balance)
        frappe.db.set_value("Item",item.item_code,"available_qty",get_item_available_qty(item.item_code))


def get_item_balance(item):
    item_balance = get_latest_stock_qty(item)
    return item_balance


def set_item_available_qty(doc,method):
    for item in doc.items:
        item_available_qty = get_item_available_qty(item.item_code)
        frappe.db.set_value("Item",item.item_code,"available_qty",item_available_qty)


def get_item_available_qty(item):
    item_available_qty = 0
    item_data = get_data(item)
    for data in item_data:
        item_available_qty += data["projected_qty"]
    return item_available_qty



@frappe.whitelist()
def recalculate_items_balance():
    items = frappe.get_all("Item")
    for item in items:
        frappe.db.set_value("Item",item.name,"balance",get_latest_stock_qty(item.name) or 0)
        frappe.db.set_value("Item",item.name,"available_qty",get_item_available_qty(item.name) or 0)


    return "Recalculate Items Balance is Done"