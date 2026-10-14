document.addEventListener('alpine:init', () => {
    Alpine.data('formSubmit', () => ({
        errors: {},
        loading: false,
        form_data: {},

        init() {
            this.form_data = this.$form?.fields || {};
        },

        set_error(field_name, message) {
            this.errors[field_name] = message;
            this.$nextTick(() => {
                let input = this.$refs[field_name] || this.$el.querySelector(`[name='${field_name}']`);
                if (input) {
                    input.classList.add('is-invalid');
                }
            });
        },

        clear_error(field_name) {
            delete this.errors[field_name];
            let input = this.$refs[field_name] || this.$el.querySelector(`[name='${field_name}']`);
            if (input) {
                input.classList.remove('is-invalid');
            }
        },

        clear_all_errors() {
            this.errors = {};
            this.$el.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        },

        validate_form() {
            this.clear_all_errors();
            let is_valid = true;

            for (let field_name in this.form_data) {
                let field = this.form_data[field_name];
                if (field.required && !this.form_data[field_name].value) {
                    this.set_error(field_name, 'This field is required');
                    is_valid = false;
                }
            }

            return is_valid;
        },

        async submit_form(event) {
            let form = event.target || this.$el;
            if (this.validate_form() && form.checkValidity()) {
                this.loading = true;
                try {
                    if (this.$form?.submit) {
                        await this.$form.submit();
                    } else {
                        form.submit();
                    }
                } catch (error) {
                    console.error('Form submission error:', error);
                } finally {
                    this.loading = false;
                }
            } else {
                form.reportValidity();
            }
        }
    }));
});

document.addEventListener('alpine:init', () => {
    Alpine.data('submitButton', () => ({
        loading: false,

        async submit_form(form) {
            if (form.checkValidity() && await this.$validation?.() !== false) {
                this.loading = true;
                try {
                    form.submit();
                } finally {
                    this.loading = false;
                }
            } else {
                form.reportValidity();
            }
        }
    }));
});
