/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
//patch the store and load the models
patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.keyboard_shortcuts = loadedData['pos.keyboard.shortcut'];
        this.payment_method_key = loadedData['pos.payment.method.key'];
    },
});
