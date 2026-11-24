document.addEventListener('alpine:init', () => {
    Alpine.data('glueField', (field, getValue, setValue) => ({
        field,

        get value() {
            return getValue();
        },

        set value(newValue) {
            setValue(newValue);
        },

        committedValue: undefined,

        // The id of the field's control, which its label is tied to. Unique on the page, so
        // the same field in each row of a formset gets its own.
        fieldId: '',

        init() {
            this.fieldId = this.$id('glue-field');
            this.committedValue = this.value;
        },

        dispatchFieldEvent(name) {
            this.$dispatch(name, {
                field: this.field,
                value: this.value,
                previousValue: this.committedValue,
            });

            if (name === 'field-change') {
                this.committedValue = this.value;
            }
        },
    }));

    // A field's wrapper reports its field's events. Focus moving between the
    // field's own elements is neither a focus nor a blur of the field.
    Alpine.bind('glueFieldEvents', () => ({
        '@input'() {
            this.dispatchFieldEvent('field-input');
        },

        '@change'() {
            this.dispatchFieldEvent('field-change');
        },

        '@focusin'(event) {
            if (!this.$el.contains(event.relatedTarget)) {
                this.dispatchFieldEvent('field-focus');
            }
        },

        '@focusout'(event) {
            if (!this.$el.contains(event.relatedTarget)) {
                this.dispatchFieldEvent('field-blur');
            }
        },
    }));

    // An input takes its name, state and validity from its field.
    Alpine.bind('glueFieldInput', () => ({
        ':id'() {
            return this.fieldId;
        },

        ':name'() {
            return this.field.name;
        },

        ':class'() {
            return { 'is-invalid': this.field.hasErrors };
        },

        ':required'() {
            return this.field.required;
        },

        ':disabled'() {
            return this.field.disabled;
        },
    }));
});
