/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
//    Pos session
patch(PosStore.prototype, {
     async _processData(loadedData) {
        await super._processData(...arguments);
        // Load field that in pos.order.question into pos.
        this.order_questions = loadedData["pos.order.question"] || [];
        }
});
