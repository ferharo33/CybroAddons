/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { cookie } from "@web/core/browser/cookie";
import { utils as uiUtils } from "@web/core/ui/ui_service";

import SurveyPreloadImageMixin from "@survey/js/survey_preload_image_mixin";

publicWidget.registry.SurveyForm = publicWidget.Widget.extend(SurveyPreloadImageMixin, {
        selector: '.o_survey_form',
        events: {
            'focus .o_select_Country': '_onSelectCountry',
            'change .o_select_Country': '_onSelectState',
            'change .o_select_many2many': '_onSelectMany2many',
        },
        init(){
            this._super(...arguments);
            this.rpc = this.bindService("rpc");
        },

        _onSelectCountry: function(ev){
            /*
                * method to load country
            */
            var self = this
            this.rpc('/survey/load_country',{})
            .then(function (result){
                var count = 0;
                self.$el.find(`#${ev.target.id}`).html('<option value="">Country</option>')
                result['id'].forEach(element => {
                    self.$el.find(`#${ev.target.id}`).append(
                    `<option value='${result['name'][count]}'>${result['name'][count]}</option>`
                    )
                    count += 1
                })
            });
        },
        _onSelectState: function(ev){
            /*
                * method to load states
            */
            var self = this
            var country_id = ev.target.value
            var question_id = ev.target.dataset.id
            this.rpc('/survey/load_states',{
            params: { country_id },
            }).then(function (result){
                var count = 0;
                self.$el.find(`#${question_id}-state`).html('<option value="">State</option>')
                result['id'].forEach(element => {
                    self.$el.find(`#${question_id}-state`).append(
                    `<option value="${result['name'][count]}">${result['name'][count]}</option>`
                    )
                    count += 1
                })
            });
        },
        _onSelectMany2many: function(ev){
         this.$el.find('.o_select_many2many_text').val(this.$el.find('.o_select_many2many').val())
        }
    });
export default publicWidget.registry.SurveyForm;
