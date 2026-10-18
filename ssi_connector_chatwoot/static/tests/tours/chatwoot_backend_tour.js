odoo.define("ssi_connector_chatwoot.chatwoot_backend_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Run-callback for steps that only assert that an element is present.
    function assertOnly() {
        // Assertion only; do not trigger the default click action.
    }

    // Field trigger usable whatever the widget root is (the input itself
    // or a wrapper that contains it).
    function fieldInput(name) {
        return (
            "input.o_field_widget[name='" +
            name +
            "'], .o_field_widget[name='" +
            name +
            "'] input"
        );
    }

    // Shared opening steps: Connector > Configuration > Chatwoot > Backends.
    // "Configuration" (level 2) is a clickable section. "Chatwoot" (level 3)
    // has children of its own, so it is a non-clickable dropdown header
    // without [data-menu-xmlid]; its leaf "Backends" is flattened into the
    // level-2 dropdown.
    function openBackendMenuSteps() {
        return [
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
                content: "Open the Backends menu",
                trigger:
                    ".o_menu_sections " +
                    '[data-menu-xmlid="ssi_connector_chatwoot.menu_chatwoot_backend"]',
            },
            {
                // Gate: wait for the TARGET action, not just any list view.
                content: "Chatwoot Backends list is displayed",
                trigger:
                    ".o_control_panel " +
                    ".breadcrumb-item.active:contains(Chatwoot Backends)",
                extra_trigger: ".o_list_view",
                run: assertOnly,
            },
        ];
    }

    // Opens the backend whose name contains the given text.
    function openBackendSteps(name) {
        return [
            {
                content: "Open the backend",
                trigger: ".o_data_row:contains(" + name + ") .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: assertOnly,
            },
        ];
    }

    // IK: docs/chatwoot_backend/01-create.md
    tour.register(
        "ssi_connector_chatwoot_chatwoot_backend_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(openBackendMenuSteps(), [
            // -- Flow 2 - Click the New button
            {
                content: "Click New",
                trigger: ".o_list_button_add",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open in edit mode",
                trigger: ".o_form_view.o_form_editable",
                run: assertOnly,
            },

            // -- Flow 3 - Fill in the fields
            {
                content: "Fill in the name",
                trigger: fieldInput("name"),
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR Create Backend",
            },
            {
                content: "Fill in the URL",
                trigger: fieldInput("url"),
                run: "text https://chatwoot.example.com",
            },
            {
                content: "Fill in the account id",
                trigger: fieldInput("account_id"),
                run: "text 5",
            },
            {
                content: "Fill in the API token",
                trigger: fieldInput("api_token"),
                run: "text tour-create-token",
            },

            // -- Flow 4 - Click Save
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: assertOnly,
            },

            // -- Post-Condition - backend shown in the list
            {
                content: "Back to the Chatwoot Backends list",
                trigger: ".breadcrumb-item.o_back_button a:contains(Chatwoot Backends)",
            },
            {
                content: "New backend is displayed in the list",
                trigger: ".o_data_row:contains(TOUR Create Backend)",
                extra_trigger: ".o_list_view",
                run: assertOnly,
            },
        ])
    );

    // IK: docs/chatwoot_backend/02-edit.md
    tour.register(
        "ssi_connector_chatwoot_chatwoot_backend_edit",
        {
            test: true,
            url: "/web",
        },
        [].concat(openBackendMenuSteps(), openBackendSteps("TOUR Edit Backend"), [
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

            // -- Flow 4 - Change the fields
            {
                content: "Change the name",
                trigger: fieldInput("name"),
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR Edit Backend Renamed",
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

            // -- Post-Condition - renamed backend shown in the list
            {
                content: "Back to the Chatwoot Backends list",
                trigger: ".breadcrumb-item.o_back_button a:contains(Chatwoot Backends)",
            },
            {
                content: "Renamed backend is displayed in the list",
                trigger: ".o_data_row:contains(TOUR Edit Backend Renamed)",
                extra_trigger: ".o_list_view",
                run: assertOnly,
            },
        ])
    );

    // IK: docs/chatwoot_backend/03-delete.md
    tour.register(
        "ssi_connector_chatwoot_chatwoot_backend_delete",
        {
            test: true,
            url: "/web",
        },
        [].concat(openBackendMenuSteps(), openBackendSteps("TOUR Delete Backend"), [
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

            // -- Post-Condition - the backend is gone
            {
                content: "Click the list breadcrumb to return to the list",
                trigger: ".breadcrumb-item.o_back_button a:contains(Chatwoot Backends)",
            },
            {
                content: "Back to the list",
                trigger: ".o_list_view",
                run: assertOnly,
            },
        ])
    );

    // IK: docs/chatwoot_backend/04-test-connection.md
    tour.register(
        "ssi_connector_chatwoot_chatwoot_backend_test_connection",
        {
            test: true,
            url: "/web",
        },
        [].concat(openBackendMenuSteps(), openBackendSteps("TOUR Test Backend"), [
            // -- Flow 3 - Click Test Connection (requests.get is patched on
            // the Python side, so no network call is made)
            {
                content: "Click Test Connection",
                trigger: ".o_statusbar_buttons button[name='action_test_connection']",
                extra_trigger: ".o_form_view",
            },

            // -- Post-Condition - success notification
            {
                content: "Success notification is displayed",
                trigger: ".o_notification:contains(Successfully connected to Chatwoot)",
                run: assertOnly,
            },
        ])
    );
});
