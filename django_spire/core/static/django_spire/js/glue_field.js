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

        init() {
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
});
