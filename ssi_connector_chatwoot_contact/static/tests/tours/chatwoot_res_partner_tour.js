odoo.define("ssi_connector_chatwoot_contact.chatwoot_res_partner_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // Shared opening steps: Connector > Chatwoot > Bindings > Contacts.
    // "Chatwoot" (level 2) is a clickable section. "Bindings" (level 3) has
    // children of its own, so it is a non-clickable dropdown header without
    // [data-menu-xmlid]; its leaf is flattened into the level-2 dropdown.
    function openBindingMenuSteps() {
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
                content: "Open the Contacts menu",
                trigger:
                    ".o_menu_sections " +
                    '[data-menu-xmlid="ssi_connector_chatwoot_contact.menu_chatwoot_contacts"]',
            },
            {
                // Gate: wait for the TARGET action, not just any list view.
                content: "Chatwoot Contact Bindings list is displayed",
                trigger:
                    ".o_control_panel " +
                    ".breadcrumb-item.active:contains(Chatwoot Contact Bindings)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ];
    }

    // IK: docs/chatwoot_res_partner/01-create.md
    tour.register(
        "ssi_connector_chatwoot_contact_chatwoot_res_partner_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(openBindingMenuSteps(), [
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
                content: "Select the partner",
                trigger: ".o_field_many2one[name='odoo_id'] input",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR Binding Create Partner",
            },
            {
                content: "Pick the partner from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Binding Create Partner)",
            },
            {
                content: "Select the backend",
                trigger: ".o_field_many2one[name='backend_id'] input",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR Chatwoot Backend",
            },
            {
                content: "Pick the backend from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Chatwoot Backend)",
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
                content: "Back to the Chatwoot Contact Bindings list",
                trigger:
                    ".breadcrumb-item.o_back_button a:contains(Chatwoot Contact Bindings)",
            },
            {
                content: "New binding is displayed in the list",
                trigger: ".o_data_row:contains(TOUR Binding Create Partner)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ])
    );

    // IK: docs/chatwoot_res_partner/02-edit.md
    tour.register(
        "ssi_connector_chatwoot_contact_chatwoot_res_partner_edit",
        {
            test: true,
            url: "/web",
        },
        [].concat(openBindingMenuSteps(), [
            // -- Flow 2 - Find and open the binding to edit
            {
                content: "Open the binding",
                trigger:
                    ".o_data_row:contains(TOUR Binding Edit Partner) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // -- Flow 3 - Click the Edit button
            {
                content: "Click the Edit button",
                trigger: ".o_form_button_edit",
            },
            {
                content: "Form is now editable",
                trigger: ".o_form_view.o_form_editable",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // -- Flow 4 - Change Chatwoot Backend
            {
                content: "Select the other backend",
                trigger: ".o_field_many2one[name='backend_id'] input",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR Chatwoot Other Backend",
            },
            {
                content: "Pick the other backend from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR Chatwoot Other Backend)",
            },

            // -- Flow 5 - Click Save
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
        ])
    );

    // IK: docs/chatwoot_res_partner/03-delete.md
    tour.register(
        "ssi_connector_chatwoot_contact_chatwoot_res_partner_delete",
        {
            test: true,
            url: "/web",
        },
        [].concat(openBindingMenuSteps(), [
            // -- Flow 2 - Find and open the binding to delete
            {
                content: "Open the binding",
                trigger:
                    ".o_data_row:contains(TOUR Binding Delete Partner) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // -- Flow 3 - Click Action > Delete
            {
                content: "Open the Action menu",
                trigger: ".o_cp_action_menus button:contains(Action)",
                run: function () {
                    this.$anchor[0].click();
                },
            },
            {
                content: "Click Delete",
                trigger: ".o_cp_action_menus .o_menu_item a",
                run: function () {
                    var $delete = $(".o_cp_action_menus .o_menu_item a").filter(
                        function () {
                            return $(this).text().trim() === "Delete";
                        }
                    );
                    $delete[0].click();
                },
            },

            // -- Flow 4 - Click OK to confirm
            {
                content: "Confirm deletion",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },

            // -- Post-Condition - the binding is gone
            {
                content: "Click the list breadcrumb to return to the list",
                trigger:
                    ".breadcrumb-item.o_back_button a:contains(Chatwoot Contact Bindings)",
            },
            {
                content: "Back to the list",
                trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ])
    );

    // IK: docs/chatwoot_res_partner/04-export.md
    tour.register(
        "ssi_connector_chatwoot_contact_chatwoot_res_partner_export",
        {
            test: true,
            url: "/web",
        },
        [].concat(openBindingMenuSteps(), [
            // -- Flow 2 - Find and open the binding to export
            {
                content: "Open the binding",
                trigger:
                    ".o_data_row:contains(TOUR Binding Export Partner) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // -- Flow 3 - Click Export to Chatwoot (requests.request is
            // patched on the Python side, so no network call is made)
            {
                content: "Click Export to Chatwoot",
                trigger: ".o_statusbar_buttons button[name='export_record']",
                extra_trigger: ".o_form_view",
            },

            // -- Post-Condition - the form is reloaded with the contact id
            {
                content: "Chatwoot Contact ID is filled",
                trigger: ".o_field_widget[name='chatwoot_id']:contains(7)",
                extra_trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ])
    );
});
