odoo.define("ssi_connector_chatwoot_message.res_users_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Run-callback for steps that only assert that an element is present.
    function assertOnly() {
        // Assertion only; do not trigger the default click action.
    }

    // IK: docs/res_users/01-set-chatwoot-notification.md
    tour.register(
        "ssi_connector_chatwoot_message_res_users_set_chatwoot_notification",
        {
            test: true,
            url: "/web",
        },
        [
            // -- Flow 1 - Open the user menu, then Preferences
            {
                content: "Open the user menu",
                trigger: ".o_user_menu a.dropdown-toggle",
            },
            {
                content: "Open Preferences",
                trigger: ".o_user_menu a[data-menu='settings']",
            },
            {
                // Gate: the Chatwoot choice exists only inside the dialog.
                content: "Preferences dialog is displayed",
                trigger:
                    ".o_field_widget[name='notification_type'] .o_radio_item:contains(Handle by Chatwoot)",
                run: assertOnly,
            },
            // -- Flow 2 - Select Handle by Chatwoot
            {
                content: "Select Handle by Chatwoot",
                trigger:
                    ".o_field_widget[name='notification_type'] .o_radio_item:contains(Handle by Chatwoot) input",
            },
            // -- Flow 3 - Select the Chatwoot inbox
            {
                content: "Type the Chatwoot inbox",
                trigger: ".o_field_widget[name='chatwoot_inbox_id'] input",
                run: "text TOUR Chatwoot Message Inbox",
            },
            {
                content: "Pick the Chatwoot inbox",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Chatwoot Message Inbox)",
            },
            // -- Flow 4 - Click Save
            {
                content: "Save the preferences",
                trigger: ".modal-footer .o_form_button_save",
            },
            // -- Post-Condition - the dialog is closed
            {
                content: "Preferences dialog is closed",
                trigger: ".o_user_menu",
                extra_trigger: "body:not(.modal-open)",
                run: assertOnly,
            },
        ]
    );
});
