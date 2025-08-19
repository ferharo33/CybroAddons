/** @odoo-module */
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { useBus, useService } from "@web/core/utils/hooks";

//Patch the Product screen and add the shortcuts on the Product screen
patch(ProductScreen.prototype, {
    setup(){
        super.setup(...arguments);
        owl.useExternalListener(document, "keydown", (ev) => {
            if (Object.keys(this.popup.popups).length === 0) {
                ev.preventDefault();
                this._product_screen_shortcuts(ev)
            }
        })
    },
    _product_screen_shortcuts(event){
        if(this.pos.config.enable_keyboard_shortcuts && this.pos.config.select_shortcut_id ){
                if (event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].customer_screen.toLowerCase()) {
                     this.pos.selectPartner();
                }
                else if(event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].select_price.toLowerCase()){
                   this.onNumpadClick('price');
                }
                else if(event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].select_discount.toLowerCase()){
                   this.onNumpadClick('discount');
                }
                else if(event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].select_qty.toLowerCase()){
                    this.onNumpadClick('quantity');
                }
                else if(event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].select_user.toLowerCase()){
                   const UserButton = document.querySelector('.username')
                     UserButton.click();
                }
                else if(event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].next_screen.toLowerCase()){
                    this.onClickPay();
                }
        }
    }
});
