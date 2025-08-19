/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/store/models";

//Patching Orderline to change the uom by adding a function.
patch(Orderline.prototype, {
        setup(_defaultObj, options) {
        super.setup(...arguments);
        this.QuestionList= this.QuestionList;
    },
    export_as_JSON(){
        var json = super.export_as_JSON.call(this);
        this.QuestionList= this.QuestionList
            return json
    },
            // Set the unit from the JSON data
    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        this.QuestionList= this.QuestionList
    },
     getDisplayData() {
        return {
            ...super.getDisplayData(),
            QuestionList: this.QuestionList
        };
    },
});

Orderline.props = {
    ...Orderline.props,
    line: {
        shape: {
            OrderQuestion: {type: String, optional: true},
        }
    }
}
