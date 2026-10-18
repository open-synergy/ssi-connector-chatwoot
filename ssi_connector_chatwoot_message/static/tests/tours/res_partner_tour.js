odoo.define("ssi_connector_chatwoot_message.res_partner_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Run-callback for steps that only assert that an element is present.
    function assertOnly() {
        // Assertion only; do not trigger the default click action.
    }

    // IK: docs/res_partner/01-set-chatwoot-notification.md
    tour.register(
        "ssi_connector_chatwoot_message_res_partner_set_chatwoot_notification",
        {
            test: true,
            url: "/web",
        },
        [
            // -- Flow 1 - Open the Contacts > Contacts menu
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Contacts app",
                trigger: '.o_app[data-menu-xmlid="contacts.menu_contacts"]',
            },
            {
                content: "Open the Contacts menu",
                trigger:
                    ".o_menu_sections " +
                    '[data-menu-xmlid="contacts.res_partner_menu_contacts"]',
            },
            {
                // Gate: wait for the TARGET action, not the app landing view.
                content: "Contacts is displayed",
                trigger: ".o_control_panel .breadcrumb-item.active:contains(Contacts)",
                extra_trigger: ".o_kanban_view",
                run: assertOnly,
            },
            // -- Flow 2 - Find and open the contact
            {
                content: "Open the contact",
                trigger: ".o_kanban_record:contains(TOUR Chatwoot Notify Partner)",
                extra_trigger: ".o_kanban_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: assertOnly,
            },
            // -- Flow 3 - Click Edit
            {
                content: "Click Edit",
                trigger: ".o_form_button_edit",
            },
            // -- Flow 4 - Open the Chatwoot Notification tab
            {
                content: "Open the Chatwoot Notification tab",
                trigger: ".o_notebook .nav-link:contains(Chatwoot Notification)",
                extra_trigger: ".o_form_view.o_form_editable",
            },
            // -- Flow 5 - Tick Notify via Chatwoot
            {
                content: "Tick Notify via Chatwoot",
                trigger:
                    ".o_notebook .tab-pane.active .o_field_widget[name='chatwoot_notify'] input",
                extra_trigger: ".o_form_view.o_form_editable",
            },
            // -- Flow 6 - Select the Chatwoot inbox
            {
                content: "Type the Chatwoot inbox",
                trigger:
                    ".o_notebook .tab-pane.active .o_field_widget[name='chatwoot_inbox_id'] input",
                run: "text TOUR Chatwoot Message Partner Inbox",
            },
            {
                content: "Pick the Chatwoot inbox",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Chatwoot Message Partner Inbox)",
            },
            // -- Flow 7 - Click Save
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },
            // -- Post-Condition - the record is saved
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: assertOnly,
            },
        ]
    );
});
