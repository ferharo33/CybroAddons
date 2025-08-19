/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
import { useService } from "@web/core/utils/hooks";
publicWidget.registry.book = publicWidget.Widget.extend({
    selector: '#book_my_vehicle',
    events: {
        'click .redirect_back_with_data':'_onClickBack',
        'click .book_now':'_onClickBook',
        'click #with_fuel':'_onClickWithFuel',
        'click #without_fuel':'_onClickWithoutFuel',
        'change #extra_km':'_onChangeExtraKm',
        'click #full_subscription':'_onClickFullPayment',
        'click #monthly_subscription':'_onClickMonthlyPayment',
    },
     init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
    },
       setup() {
        super.setup();
        this.book = useService("book");
        },
    async _onClickBook(ev){ //Click function to book subscription
        var checked= this.el.querySelector('#checkbox_for_fuel').checked
        var invoice_checked=this.el.querySelector('#checkbox_for_invoice_type').checked
        var customer_id =this.el.querySelector('input[name="customer"]').value
        var km = this.el.querySelector('#extra_km').value
        var vehicle_id = ev.currentTarget.firstChild.nextSibling.defaultValue
        await jsonrpc('/online/subscription/book', {
                    'vehicle': vehicle_id,
                    'customer':customer_id,
                    'checked':checked,
                    'invoice':invoice_checked,
                    'extra_km':km,
        }).then(function(result) {
        window.location.href="/next/vehicle/" +result.subscription_id;
    });
  },
          async _onClickWithFuel(ev){ //Click function to set  price
                this.el.querySelector('#checkbox_for_fuel').checked = true
                var km = this.el.querySelector('#extra_km').value
                var table = this.el.querySelector('#vehicle_booking_table');
                for (var i = 1, row; row = table.rows[i]; i++) {
                     for (var j = 1, col; col = row.cells[j]; j++) {
                         var current_price = row.cells[2].innerText
                         var vehicle_id = row.cells[1].getAttribute('value')
                        await  jsonrpc('/online/subscription/with/fuel',{
                                    'vehicle': vehicle_id,
                                    'price':current_price,
                                    'extra_km': km,
                         })
                         .then(function(result) {
                              row.cells[2].innerText = result
                          })
                    }
                    }
          },
            async _onClickWithoutFuel(ev){//Click function to set  price without fuel
                this.el.querySelector('#checkbox_for_fuel').checked = true
                var km = this.el.querySelector('#extra_km').value
                var table = this.el.querySelector('#vehicle_booking_table');
                for (var i = 1, row; row = table.rows[i]; i++) {
                     for (var j = 1, col; col = row.cells[j]; j++) {
                         var current_price = row.cells[2].innerText
                         var vehicle_id = row.cells[1].getAttribute('value')
                        await jsonrpc('/online/subscription/without/fuel',  {
                                    'vehicle': vehicle_id,
                                    'price':current_price,
                                    'extra_km':km,
                         })
                         .then(function(result) {
                              row.cells[2].innerText = result
                          })
                    }
                }
         },
           async _onChangeExtraKm(ev){ //Change function to set price  using extra km
                var km = ev.currentTarget.value
                var table =  this.el.querySelector('#vehicle_booking_table');
                 for (var i = 1, row; row = table.rows[i]; i++) {
                     for (var j = 1, col; col = row.cells[j]; j++) {
                         await  jsonrpc('/online/subscription/with/fuel', {
                                'extra_km': km,
                            })
                            .then(function(result){
                                row.cells[1].innerText = result
                            })
                     }
                }
        },
        _onClickFullPayment(ev){//Click function
            this.el.querySelector('#checkbox_for_invoice_type').checked = true
        },
        _onClickMonthlyPayment(ev){
           this.el.querySelector('#checkbox_for_invoice_type').checked = true
        },
        _onClickBack(){//Click function for previous page
            window.history.back();
        },
})
