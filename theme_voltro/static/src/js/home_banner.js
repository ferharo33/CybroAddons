/** @odoo-module **/

import animations from "@website/js/content/snippets.animation";
import { jsonrpc } from "@web/core/network/rpc_service";

animations.registry.get_home_banner = animations.Class.extend({
    selector: '.banner',

    start: function() {
        console.log("BANNNNER")
        this._thumbnail_Carousel()
        const actionManager = document.querySelector('#wrapwrap');
        console.log(actionManager,222222222)
        gsap.set(".rotating-image", { rotationY: -180 });
        gsap.to(".rotating-image", {
            scrollTrigger: {
                trigger: ".rotating-image",
                start: "top center",
                end: "bottom center",
                scroller: actionManager,
                scrub: true, // Controls the smoothness of the scroll-triggered animation
            },
        rotationY: 180, // Rotates the image 180 degrees
        ease: "none", // Ensures smooth continuous rotation without easing
        });
    },

    _thumbnail_Carousel() {
    console.log("WORKING")
    var mainCarousel = new Splide('#main-carousel', {
        type      : 'fade',
        rewind    : true,
        pagination: false,
        arrows    : false,
      });
    console.log(mainCarousel,"CHECK")
      // Initialize the thumbnail carousel

      var thumbnailCarousel = new Splide('#thumbnail-carousel', {
        fixedWidth  : 100,
        gap         : 10,
        rewind      : true,
        pagination  : false,
        isNavigation:  true,
        arrows:false,
      });
      console.log(thumbnailCarousel,"Check 2")
      // Synchronize the main carousel with the thumbnails
      mainCarousel.sync(thumbnailCarousel);

      // Mount the carousels
      mainCarousel.mount();
      thumbnailCarousel.mount();

    },




});







