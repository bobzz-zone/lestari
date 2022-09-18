// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gold Invoice", {
  // setup:function(frm){
  // 	frm.events.make_custom_buttons(frm);
  // },
  refresh: function (frm) {
    // your code here
    frm.events.make_custom_buttons(frm);
    if (!frm.doc.tutupan) {
      frappe.call({
        method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
        callback: function (r) {
          frm.doc.tutupan = r.message.nilai;
          refresh_field("tutupan");
        },
      });
    }
    if (frm.doc.docstatus > 0) {
      cur_frm.add_custom_button(
        __("Accounting Ledger"),
        function () {
          frappe.route_options = {
            voucher_no: frm.doc.name,
            from_date: frm.doc.posting_date,
            to_date: moment(frm.doc.modified).format("YYYY-MM-DD"),
            company: frm.doc.company,
            group_by: "Group by Voucher (Consolidated)",
            show_cancelled_entries: frm.doc.docstatus === 2,
          };
          frappe.set_route("query-report", "General Ledger");
        },
        __("View")
      );
    }
    frm.set_query("category", function (doc) {
      return {
        filters: {
          // "is_group":1
          parent_item_group: "Products",
        },
      };
    });
    frm.set_query("customer_deposit", "invoice_advance", function (doc, cdt, cdn) {
      return {
        query: "lestari.gold_selling.doctype.customer_deposit.customer_deposit.get_idr_advance",
        filters: { customer: doc.customer },
      };
    });
    frm.set_query("customer_deposit", "gold_invoice_advance", function (doc, cdt, cdn) {
      return {
        query: "lestari.gold_selling.doctype.customer_deposit.customer_deposit.get_gold_advance",
        filters: { customer: doc.customer },
      };
    });
  },
  make_custom_buttons: function (frm) {
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button(__("Quick Payment"), () => frm.events.get_gold_payment(frm));
    }
  },
  get_gold_payment: function (frm) {
    frm.call("get_gold_payment", { throw_if_missing: true }).then((r) => {
      if (r.message) {
        console.log(r.message);
        frappe.set_route("Form", r.message.doctype, r.message.name);
      }
    });
  },

  discount: function (frm) {
    if (!frm.doc.discount_amount) {
      frm.doc.discount_amount = 0;
    }
    var total = 0;
    $.each(frm.doc.items, function (i, g) {
      total = total + g.qty;
    });
    frm.doc.discount_amount = (total / 100) * frm.doc.discount;
    frm.doc.grand_total = frm.doc.total - frm.doc.discount_amount;
    if (!frm.doc.total_advance) {
      frm.doc.total_advance = 0;
    }
    frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
    refresh_field("outstanding");
    refresh_field("discount_amount");
    refresh_field("grand_total");
  },
  tutupan: function (frm) {
    var idr = 0;
    $.each(frm.doc.invoice_advance, function (i, g) {
      if (g.idr_allocated) {
        idr = idr + g.idr_allocated;
      }
    });
    frm.doc.total_idr_in_gold = idr / frm.doc.tutupan;
    frm.doc.total_advance = frm.doc.total_gold + frm.doc.total_idr_in_gold;
    frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
    refresh_field("outstanding");
    refresh_field("total_idr_in_gold");
    refresh_field("total_advance");
  },
});
frappe.ui.form.on("Gold Invoice Advance IDR", {
  idr_allocated: function (frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if (d.idr_allocated > d.idr_deposit) {
      frappe.model.set_value(cdt, cdn, "idr_allocated", 0);
      frappe.throw("Allocated cant be higher than deposit value");
    }
    var idr = 0;
    $.each(frm.doc.invoice_advance, function (i, g) {
      if (g.idr_allocated) {
        idr = idr + g.idr_allocated;
      }
    });
    frm.doc.total_idr_in_gold = idr / frm.doc.tutupan;
    frm.doc.total_advance = frm.doc.total_gold + frm.doc.total_idr_in_gold;
    frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
    refresh_field("outstanding");
    refresh_field("total_idr_in_gold");
    refresh_field("total_advance");
  },
});
frappe.ui.form.on("Gold Invoice Advance Gold", {
  gold_allocated: function (frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if (d.gold_allocated > d.gold_deposit) {
      frappe.model.set_value(cdt, cdn, "gold_allocated", 0);
      frappe.throw("Allocated cant be higher than deposit value");
    }
    var gold = 0;
    $.each(frm.doc.gold_invoice_advance, function (i, g) {
      if (g.gold_allocated) {
        gold = g.gold_allocated;
      }
    });
    frm.doc.total_gold = gold;
    frm.doc.total_advance = frm.doc.total_gold + frm.doc.total_idr_in_gold;
    frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
    refresh_field("outstanding");
    refresh_field("total_advance");
    refresh_field("total_gold");
  },
});
frappe.ui.form.on("Gold Invoice Item", {
  category: function (frm, cdt, cdn) {
    // your code here
    var d = locals[cdt][cdn];
    if (!d.category) {
      return;
    }
    frappe.call({
      method: "lestari.gold_selling.doctype.gold_invoice.gold_invoice.get_gold_rate",
      args: { category: d.category, customer: frm.doc.customer, customer_group: frm.doc.customer_group },
      callback: function (r) {
        frappe.model.set_value(cdt, cdn, "rate", r.message.nilai);
        frappe.model.set_value(cdt, cdn, "amount", (parseFloat(r.message.nilai) * d.qty) / 100);
        var total = 0;
        $.each(frm.doc.items, function (i, g) {
          total = total + g.amount;
        });
        frm.doc.total = total;
        if (!frm.doc.discount_amount) {
          frm.doc.discount_amount = 0;
        }
        frm.doc.grand_total = frm.doc.total - frm.doc.discount_amount;
        if (!frm.doc.total_advance) {
          frm.doc.total_advance = 0;
        }
        frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
        refresh_field("outstanding");
        refresh_field("total");
        refresh_field("discount_amount");
        refresh_field("grand_total");
      },
    });
  },
  qty: function (frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    frappe.model.set_value(cdt, cdn, "amount", (d.rate * d.qty) / 100);
    var total = 0;
    $.each(frm.doc.items, function (i, g) {
      total = total + g.amount;
    });
    frm.doc.total = total;
    if (!frm.doc.discount_amount) {
      frm.doc.discount_amount = 0;
    }
    frm.doc.grand_total = frm.doc.total - frm.doc.discount_amount;
    if (!frm.doc.total_advance) {
      frm.doc.total_advance = 0;
    }
    frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
    refresh_field("outstanding");
    refresh_field("total");
    refresh_field("discount_amount");
    refresh_field("grand_total");
  },
});
