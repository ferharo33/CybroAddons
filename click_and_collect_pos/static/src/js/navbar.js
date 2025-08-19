/** @odoo-module **/
import {Navbar} from "@point_of_sale/app/navbar/navbar";
import {jsonrpc} from "@web/core/network/rpc_service";
import {patch} from "@web/core/utils/patch";
import {SetSaleOrderButton} from "@pos_sale/app/set_sale_order_button/set_sale_order_button"
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
var beep = new Audio('/click_and_collect_pos/static/src/audio/notification.wav');

Navbar.components = {...Navbar.components, SetSaleOrderButton}

patch(Navbar.prototype, {
    setup() {
    super.setup();
        this.sound = useService("sound");
        this.busService = this.env.services.bus_service
        this.busService.addChannel('POS_COLLECT_ORDER')
        this.busService.addEventListener("notification", this.onMessage.bind(this))
    },

    onMessage({detail: notifications}) {
         notifications = notifications.filter(item => item.payload.channel === 'POS_COLLECT_ORDER')
          if (notifications){
              console.log("Notifications")
              this.env.services.notification.add(
                _t("One Collect Order Is Created"),
                { sticky: true ,type: "success",}
              );
              beep.play();
          }
    },
    async onClick() {
        const sale_orderSetSaleOrderButton = [];
        const stock_picking = this.pos.stock_picking;
        const session_id = this.pos.pos_session.config_id
        const sale_order_line = await jsonrpc("/web/dataset/call_kw", {
            model: "sale.order.line",
            method: "search_read",
            args: [],
            kwargs: {
                domain: [['state', '=', 'sale'], ['pos_config_id', '=', session_id[0]]],
            },
        });
        const line_ids = []
        stock_picking.forEach(function (lines) {
            lines.move_ids_without_package.forEach(function (line) {
                if (line.sale_line_id[0] && line.state !== "done") {
                    line_ids.push(line.sale_line_id[0]);
                }
            });
        });
        const sale_order = sale_order_line.filter((line) => line_ids.includes(line.id));
        this.pos.showScreen("SaleOrderScreen", {
            click_and_collect: sale_order,
        });
    },
});
