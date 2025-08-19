//** @odoo-module */
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useRef, useState } from "@odoo/owl";

patch(ProductCard.prototype, {
    setup() {
        super.setup();
        this.state = useState({
        qty_available: null,
        incoming_qty: null,
        outgoing_qty: null,
        });
        this.pos = usePos();
        this.orm = useService('orm');
        },
    async fetchProductDetails(productId) {
    const product = await this.orm.call("product.product", "read", [[productId], ["name", "id", "incoming_qty","outgoing_qty","qty_available"]]);
     return product[0];
    },
    async updateProductDetails() {
    const productId = this.props.productId;
    if (productId) {
        this.productDetail = await this.fetchProductDetails(productId);
      }
    },
     get value() {
        if (this.pos.res_setting.display_stock == true) {
            const current_product = this.props.productId;
            const stock_product = this.pos.stock_quant;
            const move_line = this.pos.move_line;
            let qty = 0;
            let on_hand = 0;
            let outgoing = 0;
            let incoming = 0;

            stock_product.forEach((product) => {
                if (product.product_id[0] === current_product) {
                    qty += product.available_quantity;
                    on_hand += product.quantity;
                }
            });
            move_line.forEach((line) => {
                 if (line.product_id[0] == current_product && this.pos.res_setting && this.pos.res_setting.stock_location_id && this.pos.res_setting.stock_location_id[1] == line.location_dest_id[1]) {
                     incoming = incoming + line.quantity;
                 } else if (line.product_id[0] == current_product && this.pos.res_setting && this.pos.res_setting.stock_location_id && this.pos.res_setting.stock_location_id[1] == line.location_id[1]) {
                      outgoing = outgoing + line.quantity;
                 }
            });
            if (!this.props.available) {
                this.props.available = qty // pass value in session
            }
            if (!this.props.on_hand) {
                this.props.on_hand = on_hand;
            }
            if (!this.props.outgoing) {
                this.props.outgoing = outgoing
            }
            if (!this.props.incoming) {
                this.props.incoming_loc = incoming
            }

            this.updateProductDetails().then(() => {
            this.state.qty_available = this.productDetail.qty_available
            this.state.incoming_qty = this.productDetail.incoming_qty
            this.state.outgoing_qty = this.productDetail.outgoing_qty
            });
            return {
                display_stock: this.pos.res_setting.display_stock

            };

        } else {
            return {
                display_stock: false
            };
        }
    }
});