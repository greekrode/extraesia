from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.utils import get_stock_balance, get_latest_stock_qty
from erpnext.stock.dashboard.item_dashboard import get_data


def set_item_balance(doc,method):
    balance = get_item_balance(doc.item_code) or 0
    balance +=  doc.actual_qty
    frappe.db.set_value("Item",doc.item_code,"balance",balance)
    frappe.db.set_value("Item",doc.item_code,"available_qty",get_item_available_qty(doc.item_code) + doc.actual_qty)

def set_item_balance_on_delete(doc,method):
    balance = get_item_balance(doc.item_code) or 0
    balance += doc.actual_qty
    frappe.db.set_value("Item",doc.item_code,"balance",balance)
    frappe.db.set_value("Item",doc.item_code,"available_qty",get_item_available_qty(doc.item_code) - doc.actual_qty)

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