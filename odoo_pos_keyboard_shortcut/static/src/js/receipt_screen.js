/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
//Patch the Receipt screen and add the shortcuts on the Receipt screen
patch(ReceiptScreen.prototype, {
    setup() {
        super.setup();
        this.receipt_screen_shortcuts();
    },
    receipt_screen_shortcuts(){
        if(this.pos.config.enable_keyboard_shortcuts){
            document.addEventListener('keydown', (event) => {
                event.preventDefault()
                if (event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].print_receipt.toLowerCase()) {
                     this.printReceipt();
                }
                 if (event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].new_order.toLowerCase()) {
                     this.orderDone();
                }
                 if (event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].resume_order.toLowerCase()) {
                     this.resumeOrder();
                }
                if (event.ctrlKey && event.key === this.pos.keyboard_shortcuts[0].sent_email.toLowerCase()) {
                     this.onSendEmail();
                }
            })
        }
    },
});
