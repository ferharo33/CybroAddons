/** @odoo-module **/
    /*Extending the public widget of the reset form for checking the user
    password strength conditions on password input function of the password field in
    the reset form,Based on the conditions from configuration settings.*/
import { jsonrpc } from "@web/core/network/rpc_service";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.SignUpFormInputPasswordChange = publicWidget.Widget.extend({
    selector: '.oe_signup_form',
    events: {
        'input input[type="password"]': '_onPasswordInput', // Listening for input event on password field
    },

    start() {
        this._super.apply(this, arguments);
    },

    _onPasswordInput: function (ev) {
        var passwordInput = ev.currentTarget;  // Get the password input field
        var current_pwd = passwordInput.value; // Get the current password value

        // Reset the progress bar if the password field is empty
        if (current_pwd.length === 0) {
            var progressBar = document.getElementById("progress");
            if (progressBar) {
                progressBar.value = "0";
                progressBar.style.backgroundColor = "#FF0000"; // Reset to red
            }
            return;
        }

        // Fetch configuration settings via jsonrpc
        jsonrpc('/web/config_params', {}).then(function (data) {
            var conditions = [];
            for (let key in data) {
                conditions.push(data[key]);
            }

            var flag = conditions.filter(cond => cond === 'True').length;

            // Evaluate password strength based on specific conditions
            var prog = [/[$@$!%*#?&]/, /[A-Z]/, /[0-9]/, /[a-z]/]
                .reduce((memo, test) => memo + test.test(current_pwd), 0);

            if (prog > 2 && current_pwd.length > 7) {
                prog++;
            }

            var progress = "0";
            var colors = ['#FF0000', '#00FF00', '#0000FF']; // Red, Green, Blue for progress levels
            var currentColor = colors[0];

            // Adjust progress based on conditions enabled
            switch (flag) {
                case 5:
                    switch (prog) {
                        case 0:
                        case 1:
                            progress = "20";
                            break;
                        case 2:
                            progress = "25";
                            break;
                        case 3:
                            progress = "50";
                            currentColor = colors[1]; // Green
                            break;
                        case 4:
                            progress = "75";
                            currentColor = colors[1]; // Green
                            break;
                        case 5:
                            progress = "100";
                            currentColor = colors[1]; // Green
                            break;
                    }
                    break;
                case 4:
                    switch (prog) {
                        case 0:
                        case 1:
                        case 2:
                            progress = "25";
                            break;
                        case 3:
                            progress = "50";
                            currentColor = colors[0]; // Red
                            break;
                        case 4:
                            progress = "75";
                            currentColor = colors[1]; // Green
                            break;
                        case 5:
                            progress = "100";
                            currentColor = colors[1]; // Green
                            break;
                    }
                    break;
                case 3:
                    switch (prog) {
                        case 0:
                        case 1:
                        case 2:
                        case 3:
                            progress = "33.33";
                            break;
                        case 4:
                            progress = "66.66";
                            currentColor = colors[1]; // Green
                            break;
                        case 5:
                            progress = "100";
                            currentColor = colors[1]; // Green
                            break;
                    }
                    break;
                case 2:
                    progress = (prog !== 5) ? "50" : "100";
                    currentColor = (prog !== 5) ? colors[0] : colors[1]; // Red or Green
                    break;
                case 1:
                    progress = "100";
                    currentColor = colors[1]; // Green
                    break;
            }

            // Update progress bar
            var progressBar = document.getElementById("progress");
            if (progressBar) {
                progressBar.value = progress;
                progressBar.style.backgroundColor = currentColor;
            }
        });
    },
});
