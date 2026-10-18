odoo.define("ssi_connector_chatwoot_message.mail_compose_message_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // Run-callback for steps that only assert that an element is present.
    function assertOnly() {
        // Assertion only; do not trigger the default click action.
    }

    // IK: docs/mail_compose_message/01-send-via-chatwoot.md
    tour.register(
        "ssi_connector_chatwoot_message_mail_compose_message_send_via_chatwoot",
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
                trigger: ".o_kanban_record:contains(TOUR Chatwoot Compose Document)",
                extra_trigger: ".o_kanban_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: assertOnly,
            },
            // -- Flow 3 - Click Send message
            {
                content: "Click Send message",
                trigger: ".o_ChatterTopbar_buttonSendMessage",
            },
            // -- Flow 4 - Click the Full composer button
            {
                content: "Click Full composer",
                trigger: ".o_Composer_buttonFullComposer",
            },
            // -- Flow 5 - Add the recipient
            {
                content: "Type the recipient",
                trigger: ".o_field_widget[name='partner_ids'] input",
                extra_trigger: ".modal .o_form_view",
                run: "text TOUR Chatwoot Compose Recipient",
            },
            {
                content: "Pick the recipient",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Chatwoot Compose Recipient)",
                // The autocomplete list is appended to <body>, outside the modal.
                in_modal: false,
            },
            // -- Flow 6 - Type the subject
            {
                content: "Type the subject",
                trigger: ".o_field_widget[name='subject']",
                run: "text TOUR Chatwoot Compose Subject",
            },
            // -- Flow 7 - Select Chatwoot in Send Via
            {
                content: "Select Chatwoot",
                trigger:
                    ".o_field_widget[name='send_via'] .o_radio_item:contains(Chatwoot) input",
            },
            // -- Flow 8 - Select the Chatwoot inbox
            {
                content: "Type the Chatwoot inbox",
                trigger: ".o_field_widget[name='chatwoot_inbox_id'] input",
                run: "text TOUR Chatwoot Compose Inbox",
            },
            {
                content: "Pick the Chatwoot inbox",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Chatwoot Compose Inbox)",
                in_modal: false,
            },
            // -- Flow 9 - Click Send
            {
                content: "Send the message",
                trigger: ".modal-footer button.o_mail_send",
            },
            // -- Post-Condition - the composer is closed
            {
                content: "Composer is closed",
                trigger: ".o_form_view",
                extra_trigger: "body:not(.modal-open)",
                run: assertOnly,
            },
        ]
    );
});
