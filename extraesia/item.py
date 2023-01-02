from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.utils import get_latest_stock_qty
from frappe.utils import getdate, today

def set_item_qty_on_hand(doc, method):
    qty_on_hand = get_item_qty_on_hand(doc.item_code) or 0
    if not doc.actual_qty:
        diff = qty_on_hand - doc.qty_after_transaction
        frappe.db.set_value("Item", doc.item_code,
                            "qty_on_hand", doc.qty_after_transaction)
        frappe.db.set_value("Item", doc.item_code, "available_qty",
                            get_item_available_qty(doc.item_code) - diff)
    else:
        qty_on_hand += doc.actual_qty
        frappe.db.set_value("Item", doc.item_code, "qty_on_hand", qty_on_hand)
        if doc.actual_qty > 0 and doc.voucher_type == "Stock Entry":
            stock_entry_type = frappe.db.get_value(
                "Stock Entry", doc.voucher_no, "stock_entry_type")
            work_order = frappe.db.get_value(
                "Stock Entry", doc.voucher_no, "work_order")
            if stock_entry_type == "Manufacture" and work_order:
                frappe.db.set_value(
                    "Item", doc.item_code, "available_qty", get_item_available_qty(doc.item_code))
            else:
                frappe.db.set_value("Item", doc.item_code, "available_qty", get_item_available_qty(
                    doc.item_code) + doc.actual_qty)
        else:
            frappe.db.set_value("Item", doc.item_code, "available_qty", get_item_available_qty(
                doc.item_code) + doc.actual_qty)


def set_item_qty_on_hand_on_delete(doc, method):
    qty_on_hand = get_item_qty_on_hand(doc.item_code) or 0
    qty_on_hand += doc.actual_qty
    frappe.db.set_value("Item", doc.item_code, "qty_on_hand", qty_on_hand)
    frappe.db.set_value("Item", doc.item_code, "available_qty",
                        get_item_available_qty(doc.item_code) - doc.actual_qty)


def set_item_qty_on_hand_after_delete_stock_reconciliation(doc, method):
    for item in doc.items:
        qty_on_hand = get_item_qty_on_hand(item.item_code) or 0
        frappe.db.set_value("Item", item.item_code, "qty_on_hand", qty_on_hand)
        frappe.db.set_value("Item", item.item_code, "available_qty",
                            get_item_available_qty(item.item_code))


def get_item_qty_on_hand(item):
    item_qty_on_hand = get_latest_stock_qty(item)
    return item_qty_on_hand or 0


def set_item_available_qty(doc, method):
    for item in doc.items:
        item_available_qty = get_item_available_qty(item.item_code)
        frappe.db.set_value("Item", item.item_code,
                            "available_qty", item_available_qty)


def get_item_available_qty(item):
    item_available_qty = 0
    item_so_qty = 0
    item_bins = frappe.db.get_all('Bin', fields=['item_code', 'reserved_qty', 'ordered_qty', 'warehouse'],
                                  or_filters={
        'projected_qty': ['!=', 0],
        'reserved_qty': ['!=', 0],
        'reserved_qty_for_production': ['!=', 0],
        'reserved_qty_for_sub_contract': ['!=', 0],
        'actual_qty': ['!=', 0],
    },
        filters={'item_code': item})
    for bin in item_bins:
        item_so_qty += bin.reserved_qty
    item_available_qty = get_item_qty_on_hand(item) - item_so_qty
    return item_available_qty


def get_item_price(item, price_list):
    conditions = "where item_code=%(item_code)s and price_list=%(price_list)s"
    condition_data_dict = dict(
        item_code=item, price_list=price_list)

    price_list_data = frappe.db.sql("""
        SELECT price_list_rate as price_list_rate, valid_from, valid_upto
        FROM `tabItem Price` 
            {conditions} order by modified asc""".format(conditions=conditions), condition_data_dict)

    price_list = 0
    for pl in price_list_data:
        valid_from = pl[1]
        valid_to = pl[2]

        if valid_to is not None:
            if valid_from <= getdate(today()) and valid_to >= getdate(today()):
                price_list = pl[0]
        elif valid_from <= getdate(today()):
                price_list = pl[0]
    
    return price_list

def update_item_price(doc, method):
    settings = frappe.get_single("Extraesia Settings")
    if not settings.item_show_price:
        return 

    if settings.price_list != doc.price_list:
        return

    if doc.valid_upto is not None:
        if getdate(doc.valid_from) <= getdate(today()) and getdate(doc.valid_to) >= getdate(today()):
            frappe.db.set_value("Item", doc.item_code, "item_price", doc.price_list_rate)
    elif getdate(doc.valid_from) <= getdate(today()):
            frappe.db.set_value("Item", doc.item_code, "item_price", doc.price_list_rate)


@ frappe.whitelist()
def recalculate_item_qty_on_hand():
    items = frappe.get_all("Item")
    for item in items:
        frappe.db.set_value("Item", item.name, "qty_on_hand",
                            get_latest_stock_qty(item.name) or 0)
        frappe.db.set_value("Item", item.name, "available_qty",
                            get_item_available_qty(item.name) or 0)

    return "Recalculate Items Qty On Hand is Done"


@ frappe.whitelist()
def set_item_price(price_list):
    items = frappe.get_all("Item")
    item_price_unset = []
    for item in items:
        if price_list == ():
            item_price_unset.append(item.name)
        else:
            frappe.db.set_value("Item", item.name, "item_price",
                                get_item_price(item.name, price_list))

    if len(item_price_unset) > 0:
        return "Please set the item price for these items and return again to set all the item price\n" + ', '.join(item_price_unset)

    return "Set Item Price is Done"