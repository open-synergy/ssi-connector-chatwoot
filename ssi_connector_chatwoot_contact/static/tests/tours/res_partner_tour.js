odoo.define("ssi_connector_chatwoot_contact.res_partner_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Shared opening steps -- Flow 1 of the base IK (ssi_partner
    // docs/res_partner/01-create.md) and of docs/res_partner/02-force-export.md:
    // "Open the Contacts > Contacts menu." The Contacts app lands on the kanban
    // view of the Contacts action.
    function openContactsMenuSteps() {
        return [
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
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ];
    }

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
            url: "/web",
        },
        [].concat(
            openContactsMenuSteps(),
            [
                // -- Flow 2 - Click the New button
                {
                    content: "Click New",
                    trigger: ".o-kanban-button-new",
                    extra_trigger: ".o_kanban_view",
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
                    // The name widget may be replaced by an installed module
                    // (partner_autocomplete): target the <input> in the title.
                    trigger: ".o_form_view .oe_title h1 input",
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
                        ".o_notebook .tab-pane.active .o_field_widget[name='sync_to_chatwoot'] input",
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
            url: "/web",
        },
        [].concat(
            openContactsMenuSteps(),
            [
                // -- Flow 2 - Find and open the partner to export
                {
                    content: "Open the partner",
                    trigger: ".o_kanban_record:contains(TOUR Chatwoot Force Partner)",
                    extra_trigger: ".o_kanban_view",
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
