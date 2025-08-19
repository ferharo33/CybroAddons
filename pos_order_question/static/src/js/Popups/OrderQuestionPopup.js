/** @odoo-module */
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import {AbstractAwaitablePopup} from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
export class OrderQuestionPopup extends AbstractAwaitablePopup {

    static template = "pos_order_question.OrderQuestionPopup";
    QuestionList = [];
    setup() {
    super.setup();
        this.pos = usePos();
    }
    _onClickCheck(ev) {
        //    This function will work when clicking on checkboxes.It will add questions of enabled check boxed into the list.
        if (ev.target.checked === true) {
            this.QuestionList.push(ev.target.parentNode.nextSibling.innerText)
        } else {
            this.QuestionList.pop(ev.target.parentNode.nextSibling.innerText)
        }
    }
    async confirm() {
        //   This function will work when clicking on ok button in the popup.It will add selected questions into order lines.
        const selectedOrderline = this.pos.get_order().get_selected_orderline();
        selectedOrderline.QuestionList = this.QuestionList
        this.cancel();
    }
}
