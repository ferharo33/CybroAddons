/** @odoo-module */
import Animation from "@website/js/content/snippets.animation";

Animation.registry.testimonial = Animation.Class.extend({
    selector : '.testimonial-section',
    start: function(){
    var self = this;
    self.testimonial_carousel();
    },
    testimonial_carousel: function () {
        var self= this;
        this.$("#testimonial_carousel").owlCarousel({
            items: 2,
            loop: true,
            nav: false,
            autoplay: true,
            dots: true,
        });
        },
        });
