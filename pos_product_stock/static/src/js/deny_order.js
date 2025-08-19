/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    async addProductToCurrentOrder(event) {
        if (event.detailed_type === 'product') {
            if (this.res_setting['stock_from'] === 'all_warehouse') {
                if (this.res_setting['stock_type'] === 'on_hand') {
                    if (event.qty_available <= event.deny) {
                        await this.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t('%s is Out Of Stock', event.display_name),
                        });
                    } else {
                        super.addProductToCurrentOrder(event);
                    }
                } else if (this.res_setting['stock_type'] === 'outgoing_qty') {
                    if (event.outgoing_qty <= event.deny) {
                        await this.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t('%s is Out Of Stock', event.display_name),
                        });
                    } else {
                        super.addProductToCurrentOrder(event);
                    }
                } else if (this.res_setting['stock_type'] === 'incoming_qty') {
                    if (event.incoming_qty <= event.deny) {
                        await this.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t('%s is Out Of Stock', event.display_name),
                        });
                    } else {
                        super.addProductToCurrentOrder(event);
                    }
                }
            } else if (this.res_setting['stock_from'] === 'current_warehouse') {
                if (this.res_setting['stock_type'] === 'on_hand') {
                    if (event.qty_available <= event.deny) {
                        await this.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t('%s is Out Of Stock', event.display_name),
                        });
                    } else {
                        super.addProductToCurrentOrder(event);
                    }
                } else if (this.res_setting['stock_type'] === 'outgoing_qty') {
                    if (event.outgoing_qty <= event.deny) {
                        await this.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t('%s is Out Of Stock', event.display_name),
                        });
                    } else {
                        super.addProductToCurrentOrder(event);
                    }
                } else if (this.res_setting['stock_type'] === 'incoming_qty') {
                    if (event.incoming_qty <= event.deny) {
                        await this.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t('%s is Out Of Stock', event.display_name),
                        });
                    } else {
                        super.addProductToCurrentOrder(event);
                    }
                }
            }
        } else {
            super.addProductToCurrentOrder(event);
        }
    },
});