/** @odoo-module */
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ShortcutPopup } from "./shortcut_popup.js";
import { ErrorPopup } from "./error_popup.js";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { Component ,useState} from "@odoo/owl";
/**
* This class represents a custom button in the Point of Sale product screen.
*/
export class ShortcutButton extends Component {
   static template = "pos_keyboard_shortcut.Shortcuts";
    /**
    * Initializes the component and sets up necessary dependencies.
    */
   setup() {
       this.pos = usePos();
       this.popup = useService("popup");
   }
    /**
    * Handles the click event of the Custom button.
    * Opens a popup for adding products and updates the order.
    */
   async click() {
   if (this.pos.config.select_shortcut_id){
       const order = this.pos.get_order();
       await this.popup.add(ShortcutPopup, {
               title: _t("Pos Keyboard Shortcuts"),
           });
           }
   else {
        await this.popup.add(ErrorPopup, {
            title: _t("Warning"),

        });
    }
   }
}
// Adds the custom button to the ProductScreen controls.
ProductScreen.addControlButton({
   component: ShortcutButton,
   condition: function () {
       return true;
   },
});
