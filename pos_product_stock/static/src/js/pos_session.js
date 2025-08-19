/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
        async _processData(loadedData) {
            super._processData(...arguments); //used to call the original _processData
            this.res_setting = loadedData['res.config.settings'];
            this.stock_quant = loadedData['stock.quant'];
            this.move_line = loadedData['stock.move.line'];
        }
    })