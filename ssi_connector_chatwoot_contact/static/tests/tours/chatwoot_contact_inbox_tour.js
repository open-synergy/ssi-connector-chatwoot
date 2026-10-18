odoo.define("ssi_connector_chatwoot_contact.chatwoot_contact_inbox_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // Shared opening steps: Connector > Chatwoot > Bindings > Contact Inboxes.
    // "Chatwoot" (level 2) is a clickable section. "Bindings" (level 3) has
    // children of its own, so it is a non-clickable dropdown header without
    // [data-menu-xmlid]; its leaf is flattened into the level-2 dropdown.
    function openContactInboxMenuSteps() {
        return [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Connector app",
                trigger: '.o_app[data-menu-xmlid="ssi_connector.menu_root_connector"]',
            },
            {
                content: "Open the Chatwoot menu",
                trigger:
                    ".o_menu_sections " +
                    '[data-menu-xmlid="ssi_connector_chatwoot.menu_chatwoot_root"]',
            },
            {
                content: "Open the Contact Inboxes menu",
                trigger:
                    ".o_menu_sections " +
                    '[data-menu-xmlid="ssi_connector_chatwoot_contact.menu_chatwoot_contact_inbox"]',
            },
            {
                // Gate: wait for the TARGET action, not just any list view.
                content: "Chatwoot Contact Inbox Bindings list is displayed",
                trigger:
                    ".o_control_panel " +
                    ".breadcrumb-item.active:contains(Chatwoot Contact Inbox Bindings)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ];
    }

    // IK: docs/chatwoot_contact_inbox/01-create.md
    tour.register(
        "ssi_connector_chatwoot_contact_chatwoot_contact_inbox_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(openContactInboxMenuSteps(), [
            // -- Flow 2 - Click the New button
            {
                content: "Click New",
                trigger: ".o_list_button_add",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open in edit mode",
                trigger: ".o_form_view.o_form_editable",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // -- Flow 3 - Fill in the required fields
            {
                content: "Select the contact binding",
                trigger: ".o_field_many2one[name='partner_binding_id'] input",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR CI Create Partner",
            },
            {
                content: "Pick the contact binding from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR CI Create Partner)",
            },
            {
                content: "Select the inbox",
                trigger: ".o_field_many2one[name='inbox_id'] input",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR CI Inbox",
            },
            {
                content: "Pick the inbox from the dropdown",
                trigger: ".ui-autocomplete .ui-menu-item a:contains(TOUR CI Inbox)",
            },

            // -- Flow 4 - Click Save
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // -- Post-Condition - binding shown in the list
            {
                content: "Back to the Chatwoot Contact Inbox Bindings list",
                trigger:
                    ".breadcrumb-item.o_back_button a:contains(Chatwoot Contact Inbox Bindings)",
            },
            {
                content: "New binding is displayed in the list",
                trigger: ".o_data_row:contains(TOUR CI Create Partner)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ])
    );

    // IK: docs/chatwoot_contact_inbox/02-export.md
    tour.register(
        "ssi_connector_chatwoot_contact_chatwoot_contact_inbox_export",
        {
            test: true,
            url: "/web",
        },
        [].concat(openContactInboxMenuSteps(), [
            // -- Flow 2 - Find and open the binding to export
            {
                content: "Open the binding",
                trigger:
                    ".o_data_row:contains(TOUR CI Export Partner) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // -- Flow 3 - Click Export (the export is only queued)
            {
                content: "Click Export",
                trigger: ".o_statusbar_buttons button[name='action_export']",
                extra_trigger: ".o_form_view",
            },

            // -- Post-Condition - the export is queued
            {
                content: "Export queued notification is displayed",
                trigger:
                    ".o_notification:contains(The contact inbox export has been queued)",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ])
    );
});
