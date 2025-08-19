/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { onWillStart ,useState} from "@odoo/owl";
import { ProductCatalogOrderLine} from "@product/product_catalog/order_line/order_line";
import {useService} from "@web/core/utils/hooks"
 /**
 * This patch extends the ProductCatalogOrderLine component to check if the current user
 * belongs to a specific group ('hide_product_price_cost.hide_product_price_cost_group_user_show_product_price').
 **/
patch(ProductCatalogOrderLine.prototype, {
    setup(){
    super.setup();
    this.user = useService("user");
     onWillStart(async () => {
     // Check if the user belongs to the specified group
            this.userHasGroup =await this.user.hasGroup('hide_product_price_cost.hide_product_price_cost_group_user_show_product_price');
        });
    }
});