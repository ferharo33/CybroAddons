/* @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToElement } from "@web/core/utils/render";
import '@website_sale/js/website_sale_delivery';
import { useRef, useState } from "@odoo/owl";


/**
 * Extends the websiteSaleDelivery widget to handle store pickup functionality.
 */
publicWidget.registry.websiteSaleDelivery.include({

    start: function () {
    this.rpc = this.bindService("rpc");
    return this._super.apply(this, ...arguments);
    },
    /**
     * Handles the click event on the store pickup dropdown.
     *
     * Updates the address display based on the selected store and toggles the
     * visibility of UI elements.
     *
     * @param {Event} ev - The click event.
     */
      async _onClickDropDown(ev){
        var addressTemplate = {};
        const selectedStoreId = parseInt(ev.target.selectedOptions[0]?.dataset.storeId)
        var self = this;
        const address = await this.rpc( '/shop/update_address', {
                store_id: selectedStoreId
                })
        this.$el.find('#store_address_section').remove()
        if (address) {
            addressTemplate.address = address.store_id[0].contact_address
        }
        this.$el.find('#shipping_and_billing').after(renderToElement('StoreAddress', addressTemplate));
        this.$el.find('#shipping_and_billing').hide();
    },
    /**
     * Handles the click event on a carrier option.
     *
     * Performs actions such as checking carrier options, updating UI elements,
     * and dynamically rendering store pickup dropdown.
     *
     * @param {Event} ev - The click event.
     */
     _onCarrierClick: async function (ev) {
            this._super(...arguments)
            var radio = $(ev.currentTarget).find('input[type="radio"]');
            const status = await this.rpc( '/shop/check_carrier', {
                    carrier_id: radio.val()
                }
            )
            this.$el.find('#shipping_and_billing').show()
            this.$el.find('#store_address_section').remove()
            if (this.$el.find('#shipping_and_billing'))
                var storeDropdown = this.$el.find('.store-pickup-dropdown');
                if (! status.is_store_pick ){
                    storeDropdown.hide();
                }
                if (status['is_store_pick']){
                    var templateData = {};
                    if (status['store_ids'].length === 0) {
                        templateData.store_all = status['store_id'];
                    }
                    else {
                        templateData.stores = status['store_ids'];
                    }
                    var self = this;
                    if ( storeDropdown.length === 0 ) {
                        await this.$el.find('#delivery_method').append(renderToElement('StorePickup', templateData));
                        this.el.querySelector('.store-pickup-dropdown').addEventListener('click',this._onClickDropDown.bind(this) )
                        storeDropdown.on('click', this._onClickDropDown.bind(this))
                    }
                    else {
                        storeDropdown.show()
                    }
                }
    }
})
