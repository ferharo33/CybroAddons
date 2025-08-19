/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
//Patch the payment screen and add the shortcuts on the payment screen
patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.payment_screen_shortcuts();
    },
    payment_screen_shortcuts(){
        if(this.pos.config.enable_keyboard_shortcuts){
            document.addEventListener('keydown', (event) => {
                event.preventDefault()
                if (event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].select_invoice.toLowerCase()) {
                   const InvoiceButton = document.querySelector('.js_invoice')
                   InvoiceButton.click();
                }
                 if (event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].back_screen.toLowerCase()) {
                   const BackButton = document.querySelector('.back')
                   BackButton?.click();
                }
                if (this.pos.payment_method_key[0]){
                    if (event.ctrlKey && event.key === this.pos.payment_method_key[0].key_code.toLowerCase()) {
                       const Payment_method = document.querySelector('.payment-method-display')
                       Payment_method.click();
                    }
                 }
                 if (event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].validate_order.toLowerCase()) {
                   this.validateOrder();
                }
            })
        }
    },
});
