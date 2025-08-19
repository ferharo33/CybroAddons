/** @odoo-module **/
import { jsonrpc } from "@web/core/network/rpc_service";
import { patch } from "@web/core/utils/patch";
import { CrossProduct } from "@pos_pro_cross_selling/app/cross_product/cross_product";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ErrorBarcodePopup } from "@point_of_sale/app/barcode/error_popup/barcode_error_popup";

// Function to get cross-selling products for a given product
async function getCrossSellingProducts(productId) {
    const result = await jsonrpc('/web/dataset/call_kw/pos.cross.selling/get_cross_selling_products', {
        model: 'pos.cross.selling',
        method: 'get_cross_selling_products',
        args: [[], productId],
        kwargs: {},
    });
    return result;
  }
patch(ProductScreen.prototype, {
      /**
     * @overwrite
     */
       async _barcodeProductAction(code) {
        const product = await this._getProductByBarcode(code);
        if (!product) {
            return this.popup.add(ErrorBarcodePopup, { code: code.base_code });
        }
        const result = await getCrossSellingProducts(product.id);
        if (result.length >0) {
              await this.popup.add(CrossProduct, {
                      product: result
              });
        }
        const options = await product.getAddProductOptions(code);
        if (!options) {
            return;
        }
        if (code.type === "price") {
            Object.assign(options, {
                price: code.value,
                extras: {
                    price_type: "manual",
                },
            });
        } else if (code.type === "weight" || code.type === "quantity") {
            Object.assign(options, {
                quantity: code.value,
                merge: false,
            });
        } else if (code.type === "discount") {
            Object.assign(options, {
                discount: code.value,
                merge: false,
            });
        }
        this.currentOrder.add_product(product, options);
        this.numberBuffer.reset();
    }
});