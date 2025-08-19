/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { Component, useState , useRef, useEffect } from "@odoo/owl";
import { animations } from "@website/js/content/snippets.animation";
const { DateTime } = luxon;
import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToFragment } from "@web/core/utils/render";
import { useService } from "@web/core/utils/hooks";
import { jsonrpc } from "@web/core/network/rpc_service";
import { DateTimePicker } from "@web/core/datetime/datetime_picker";


const DATE_FORMAT = "yyyy-MM-dd";
const DATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss";

publicWidget.registry.CustomCalendar = publicWidget.Widget.extend({
    selector: '.s_event_calendar_list',

    setup() {
        const rpc = useService("rpc");
    },

    init: function () {
        const referenceMoment = DateTime.local().setLocale("en");
        this.selected_date = null

        this.datepickerOptions = {
            inline: true,
            minDate: referenceMoment.minus({ years: 100 }),
            maxDate: referenceMoment.plus({ years: 100 }),
            icons: {
                previous: "fa fa-chevron-left",
                next: "fa fa-chevron-right",
            },
            format: DATE_FORMAT,
            useCurrent: false,
            locale: referenceMoment.loc.locale,
        };

        return this._super.apply(this, arguments);
    },

    start: function (editableMode) {
        this._super.apply(this, arguments);

        if (editableMode) {
            return;
        }
        this.selectedDates = {
            min: null,
            max: null,
            matches: [],
        };

        this.defaultAmount = Number(this.$(".js_amount").html()) || 4;
        // Get initial events to render the list
        this.loadEvents(null, this.defaultAmount)
            .then($.proxy(this, "renderList"));
        // Preload dates and render the calendar
        const referenceMoment = DateTime.local().setLocale("en");
        this.preloadDates(referenceMoment)
            .then($.proxy(this, "renderCalendar"));
    },

    preloadDates: function (when) {
        const referenceMoment = DateTime.local().setLocale("en");
        const margin = { months: 4 };

        // Don't preload if we have up to 4 months of margin
        if (
            this.selectedDates.min && this.selectedDates.max &&
            this.selectedDates.min <= when - margin &&
            this.selectedDates.max >= when + margin
        ) {
            return $.Deferred().resolve();
        }
        // Default values
        margin.months += 2;
        const start = referenceMoment.minus(margin);
        const end = referenceMoment.plus(margin);
        // If we already preloaded, preload 6 more months
        if (this.selectedDates.min) {
            start.subtract(6, "months");
        }
        if (this.selectedDates.max) {
            end.add(6, "months");
        }
        // Do the preloading
        return this.loadDates(start, end);
    },

    loadDates: function (start, end) {
            const startdate = start.toISO();

            return jsonrpc(
                "/web_events_calendar_view/days_with_events",
                {
                    start: start.toISO(),
                    end: end.toISO(),
                }
            ).then($.proxy(this, "updateDatesCache", start, end));
        },

    updateDatesCache: function (start, end, dates) {
            if (!this.selectedDates.min || this.selectedDates.min > start) {
                this.selectedDates.min = start;
            }
            if (!this.selectedDates.max || this.selectedDates.max < end) {
                this.selectedDates.max = end;
            }
            this.selectedDates.matches = [...new Set([...this.selectedDates.matches, ...dates])];

        },

    renderCalendar: function () {
        const enabledDates = this.selectedDates.matches.map((ndate) => {
            return new Date(ndate); // Convert string date to JavaScript Date object
        });
        this._load_fullcalendar();
    },

    _load_fullcalendar: function () {
        // Dynamically load FullCalendar CSS
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = 'https://cdn.jsdelivr.net/npm/fullcalendar@5.10.0/main.min.css';
        document.head.appendChild(link);

        // Dynamically load FullCalendar JS
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://cdn.jsdelivr.net/npm/fullcalendar@5.10.0/main.min.js';
        script.onload = this._initialize_calendar.bind(this);  // Initialize the calendar once the script is loaded
        document.body.appendChild(script);
    },

    async _initialize_calendar() {
        var calendarElement = document.querySelector('.s_event_calendar')
        if (!calendarElement) {
            return;
        }

         var events = await jsonrpc(
                "/web_events_calendar_view/events",
                {}
            );

        // Initialize FullCalendar
        new FullCalendar.Calendar(calendarElement, {
            initialView: 'dayGridMonth',
            events: events,

            // This will trigger when a date is clicked
            dateClick: (info) => {
                this.handleDateClick(info);  // 'this' now refers to the CalendarHandler instance
            }
        }).render();
    },

    // Handle date click event
    handleDateClick(info) {
        let clickedDate = info.dateStr;  // Date in 'YYYY-MM-DD' format
        this.selected_date = clickedDate;

        let previousSelectedDate = document.querySelector('.fc-selected');
        if (previousSelectedDate) {
            previousSelectedDate.classList.remove('fc-selected');
            previousSelectedDate.style.backgroundColor = ''; // Reset background color
        }

        // Add background color to the clicked date
        let clickedDateElement = info.dayEl; // Get the actual DOM element of the clicked day
        clickedDateElement.classList.add('fc-selected');
        clickedDateElement.style.backgroundColor = '#1b918b';

        // Get the default amount
        this.defaultAmount = Number(document.querySelector(".js_amount").innerHTML) || 4;

        // Call loadEvents and then render the list
        this.loadEvents(this.selected_date, this.defaultAmount)
            .then(this.renderList);
    },

    renderList: function (events) {
        document.querySelector('.s_event_list').innerHTML = '';

        document.querySelector('.s_event_list').append(renderToFragment(
            'web_events_calendar_view.list',
            {
            events: events
            }
        ));
    },

    loadEvents: function (day, limit) {
        return jsonrpc(
            "/web_events_calendar_view/events_for_day",
            {day: day, limit: limit}
        );
    },

});
