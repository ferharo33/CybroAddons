/** @odoo-module **/

import animations from "@website/js/content/snippets.animation";
import { jsonrpc } from "@web/core/network/rpc_service";

animations.registry.get_home_banner = animations.Class.extend({
    selector: '.brands',

    start: function() {
    this.$('#brands').owlCarousel({
                items: 4,             // Show 4 items at a time
                loop: true,           // Enable continuous loop mode
                margin: 20,           // Space between items
                autoplay: true,       // Enable auto scroll
                autoplayTimeout: 3000, // Time interval for auto scroll (3 seconds)
                autoplayHoverPause: true, // Pause on hover
                dots: false,          // Disable dots
                nav: false,
                responsive: {
                  0: {
                    items: 1              // Show 1 item for screen widths 0px and up
                  },
                  600: {
                    items: 2               // Show 2 items for screen widths 600px and up
                  },
                  1000: {
                    items: 5                // Show 3 items for screen widths 1000px and up
                  }
                }
        });

    },


});