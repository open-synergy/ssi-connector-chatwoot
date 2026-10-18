odoo.define("ssi_connector_chatwoot_contact.res_partner_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // The Contacts menu is provided by the optional Contacts app, which is
    // not a dependency of this module and is therefore not installed in the
    // test database. The tours open the very same partner list action
    // through its URL (action XML ID, list view) instead of through the menu
    // (Flow 1 of the IK).
    var PARTNER_LIST_URL = "/web#action=base.action_partner_form&view_type=list";

    function openChatwootTabSteps() {
        return [
            {
                content: "Open the Chatwoot tab",
                trigger: ".o_notebook .nav-link:contains(Chatwoot)",
                extra_trigger: ".o_form_view",
            },
            {
                content: "Chatwoot tab is displayed",
                trigger:
                    ".o_notebook .tab-pane.active .o_field_widget[name='chatwoot_bind_ids']",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ];
    }

    // IK: docs/res_partner/01-create.md
    tour.register(
        "ssi_connector_chatwoot_contact_res_partner_create",
        {
            test: true,
            url: PARTNER_LIST_URL,
        },
        [].concat(
            [
                {
                    content: "Partner list is displayed",
                    trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click action.
                    },
                },
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
                    content: "Fill in Name",
                    trigger: ".o_field_widget[name='name']",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text TOUR Chatwoot Created Partner",
                },
            ],
            // -- Flow 4 - Open the Chatwoot tab
            [
                {
                    content: "Open the Chatwoot tab",
                    trigger: ".o_notebook .nav-link:contains(Chatwoot)",
                    extra_trigger: ".o_form_view.o_form_editable",
                },
                // -- Flow 5 - Enable Sync to Chatwoot
                {
                    content: "Enable Sync to Chatwoot",
                    trigger:
                        ".o_notebook .tab-pane.active .o_field_boolean[name='sync_to_chatwoot'] input",
                    extra_trigger: ".o_form_view.o_form_editable",
                },
                // -- Flow 6 - Click Save
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
                // -- Post-Condition - one binding per active backend is listed
                {
                    content: "A binding is listed on the Chatwoot tab",
                    trigger:
                        ".o_notebook .tab-pane.active .o_field_widget[name='chatwoot_bind_ids'] .o_data_row",
                    run: function () {
                        // Assertion only; do not trigger the default click action.
                    },
                },
            ]
        )
    );

    // IK: docs/res_partner/02-force-export.md
    tour.register(
        "ssi_connector_chatwoot_contact_res_partner_force_export",
        {
            test: true,
            url: PARTNER_LIST_URL,
        },
        [].concat(
            [
                // -- Flow 2 - Find and open the partner to export
                {
                    content: "Open the partner",
                    trigger:
                        ".o_data_row:contains(TOUR Chatwoot Force Partner) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only; do not trigger the default click action.
                    },
                },
            ],
            // -- Flow 3 - Open the Chatwoot tab
            openChatwootTabSteps(),
            [
                // -- Flow 4 - Click Force Export to Chatwoot
                {
                    content: "Click Force Export to Chatwoot",
                    trigger: "button[name='action_force_export_to_chatwoot']",
                    extra_trigger: ".o_form_view",
                },
                // -- Post-Condition - the binding is listed
                {
                    content: "A binding is listed on the Chatwoot tab",
                    trigger:
                        ".o_notebook .tab-pane.active .o_field_widget[name='chatwoot_bind_ids'] .o_data_row",
                    run: function () {
                        // Assertion only; do not trigger the default click action.
                    },
                },
            ]
        )
    );
});
