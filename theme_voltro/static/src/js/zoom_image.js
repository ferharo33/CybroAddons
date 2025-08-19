/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";


publicWidget.registry.zoomImage = publicWidget.Widget.extend({
        selector: ".voltro_product_images",

//      events: {
//        'mousemove .preview_wrapp': '_onZoomImage',
//      },

    // Define the events to be handled by the widget
    start: function () {
        var self = this;
        // Get the preview images
        var $images = this.$('.preview_image');
        // Hide images if there are more than 4
        if ($images.length > 4) {
            $images.slice(4).hide();
        }
    },

//    _onZoomImage:function(){
//        const driftImgs = this.$('.zoom-image');
//            driftImgs.each((index, img) => {
//            new Drift(img, {
//                // Use the `.detail` container to control where the pane appears
//                paneContainer: document.querySelector('.detail'),
//                // Disable inline pane to make it appear outside the image
//                inlinePane: false,
//                // Show a bounding box around the area being zoomed in
//                hoverBoundingBox: false,
//                // Zoom factor (adjust if necessary)
//                zoomFactor: 2,
//                // No need for inline options as the pane is already outside
//                containInline: true,
//                // Adjusts the pane position to appear on the right of the image
//                paneOffsetX: 500, // This controls the distance of the zoom pane from the image
//            });
//        });
//        // Apply Drift zoom to each image
//
//    }
});;