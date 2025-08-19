/** @odoo-module */
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
/**
* This class represents a custom popup in the Point of Sale.
* It extends the AbstractAwaitablePopup class.
*/
export class ShortcutPopup extends AbstractAwaitablePopup {
   static template = "pos_keyboard_shortcut.ShortcutPopup";
   static defaultProps = {
       cancelText: _t("Close"),
       title: _t("POS KEYBOARD SHORTCUTS"),
   };
}
