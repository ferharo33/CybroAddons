# -*- coding: utf-8 -*-
###############################################################################
#
# Cybrosys Technologies Pvt. Ltd.
#
# Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
# Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
# You can modify it under the terms of the GNU AFFERO
# GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
# You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
# (AGPL v3) along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Theme Shopping',
    'version': '17.0.1.0.1',
    'category': 'Theme/eCommerce',
    'summary': "Theme Shopping is an attractive and modern eCommerce Website "
               "theme",
    'description': "Theme Shopping is new kind of Theme.The theme is very "
                   "user-friendly"
                   "and suitable for your eCommerce website with blog",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['sale_management', 'website_blog', 'website_sale_wishlist',
                'website_sale',
                'website_sale_comparison', 'website_mass_mailing'],
    'data': [
        'views/header_templates.xml',
        'views/homepage.xml',
        'views/footer_templates.xml',
        'views/about_us_views.xml',
        'views/blog_templates.xml',
        'views/snippets/frequently_asked.xml',
        'views/snippets/our_team.xml',
        'views/snippets/testimonial_snippet.xml',
        'views/snippets/offers.xml',
        'views/snippets/winter_collections.xml',
        'views/snippets/price_collection.xml',
        'views/snippets/subscription.xml',
        'views/shop_templates.xml',
        'views/snippets.xml',
        'views/product_template_views.xml',
        'views/snippets/top_deal_carousal_templates.xml',
        'views/website_sale_wishlist_template.xml',
        'data/ir_cron.xml',
    ],
    'demo': ['data/product_category_data.xml'],
    'assets': {
        'web.assets_frontend': [
            "theme_shopping/static/src/js/top_deal_carousel/"
            "top_deal_carousal.js",
            "theme_shopping/static/src/js/winter_collection_carousel/"
            "winter_products_carousel.js",
            "theme_shopping/static/src/js/testimonial.js",
            "theme_shopping/static/src/js/subscription/subscription.js",
            "theme_shopping/static/src/js/snippet_carousel.js",
            "theme_shopping/static/src/css/main.css",
            "theme_shopping/static/src/css/owl.carousel.min.css",
            "theme_shopping/static/src/css/owl.theme.default.min.css",
            "theme_shopping/static/src/js/owl.carousel.js",
            "theme_shopping/static/src/js/owl.carousel.min.js",
        ],
    },
    'images': [
        'static/description/banner.jpg',
        'static/description/theme_screenshot.jpg',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
