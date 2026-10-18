odoo.define("ssi_connector_chatwoot.chatwoot_inbox_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Run-callback for steps that only assert that an element is present.
    function assertOnly() {
        // Assertion only; do not trigger the default click action.
    }

    // IK: docs/chatwoot_inbox/01-edit.md
    tour.register(
        "ssi_connector_chatwoot_chatwoot_inbox_edit",
        {
            test: true,
            url: "/web",
        },
        [
            // -- Flow 1 - Open Connector > Configuration > Inboxes. The
            // "Inboxes" leaf is flattened into the level-2 dropdown.
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Connector app",
                trigger: '.o_app[data-menu-xmlid="ssi_connector.menu_root_connector"]',
            },
            {
                content: "Open the Configuration menu",
                trigger:
                    ".o_menu_sections " +
                    '[data-menu-xmlid="ssi_connector.menu_connector_configuration"]',
            },
            {
                content: "Open the Inboxes menu",
                trigger:
                    ".o_menu_sections " +
                    '[data-menu-xmlid="ssi_connector_chatwoot.menu_chatwoot_inbox"]',
            },
            {
                // Gate: wait for the TARGET action, not just any list view.
                content: "Chatwoot Inboxes list is displayed",
                trigger:
                    ".o_control_panel " +
                    ".breadcrumb-item.active:contains(Chatwoot Inboxes)",
                extra_trigger: ".o_list_view",
                run: assertOnly,
            },

            // -- Flow 2 - Open the inbox
            {
                content: "Open the inbox",
                trigger: ".o_data_row:contains(TOUR Inbox) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: assertOnly,
            },

            // -- Flow 3 - Click the Edit button
            {
                content: "Click the Edit button",
                trigger: ".o_form_button_edit",
            },
            {
                content: "Form is now editable",
                trigger: ".o_form_view.o_form_editable",
                run: assertOnly,
            },

            // -- Flow 4 - Tick Allow Outgoing Messages
            {
                content: "Tick Allow Outgoing Messages",
                trigger: ".o_field_widget[name='allow_outgoing'] input",
                extra_trigger: ".o_form_view.o_form_editable",
            },

            // -- Flow 5 - Click Save
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: assertOnly,
            },
        ]
    );
});
