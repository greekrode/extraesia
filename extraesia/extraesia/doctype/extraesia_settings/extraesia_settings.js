// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on("Extraesia Settings", {
  onload: function (frm) {
    if (frm.doc.calculate_item_stock_level === 1) {
      frm.set_df_property("recalculate_item_qty_on_hand", "hidden", 0);
    }

    if (frm.doc.item_show_price === 1) {
      frm.set_df_property("price_list", "hidden", 0);
      frm.set_df_property("price_list", "reqd", 1);
      frm.set_df_property("set_item_price", "hidden", 0);
    }
  },
  calculate_item_stock_level: function (frm) {
    if (frm.doc.calculate_item_stock_level === 1) {
      frm.set_df_property("recalculate_item_qty_on_hand", "hidden", 0);
    }
  },
  recalculate_item_qty_on_hand: function (frm) {
    frappe.call({
      method: "extraesia.item.recalculate_item_qty_on_hand",
      callback: function (r) {
        if (!r.exc) {
          frappe.msgprint(r.message);
        }
      },
    });
  },
  item_show_price: function (frm) {
    if (frm.doc.item_show_price === 1) {
      frm.set_df_property("price_list", "hidden", 0);
      frm.set_df_property("price_list", "reqd", 1);
      frm.set_df_property("set_item_price", "hidden", 0);
      frm.set_query("price_list", function () {
        return {
          filters: [["Price List", "enabled", "=", "1"]],
        };
      });
    }
  },
  set_item_price: function (frm) {
    if (frm.doc.price_list !== undefined || frm.doc.price_list !== "") {
      frappe.call({
        method: "extraesia.item.set_item_price",
        args: {
          price_list: frm.doc.price_list,
        },
        callback: function (r) {
          if (!r.exc) {
            frappe.msgprint(r.message);
          }
        },
      });
    } else {
      frappe.msgprint("Please Choose the Price List!");
    }
  },
});
