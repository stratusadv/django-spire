document.addEventListener('alpine:init', () => {
    Alpine.data('multiSearchAndSelect', (glueField) => ({
        isOpen: false,
        search: '',

        get selectedChoices() {
            return glueField?.selectedChoices || [];
        },

        get filteredChoices() {
            if (glueField?.choices_searchable && glueField.isSearchingChoices) return [];

            const selectedValues = new Set(this.selectedChoices.map(choice => String(choice.value)));
            const query = this.search.trim().toLowerCase();
            return (glueField?.choices || []).filter(choice =>
                !selectedValues.has(String(choice.value))
                && (
                    glueField?.choices_searchable
                    || String(choice.label).toLowerCase().includes(query)
                )
            );
        },

        open() {
            if (glueField.disabled) return;
            this.search = '';
            glueField.clearSearch?.();
            this.isOpen = true;
            this.$nextTick(() => this.$refs.searchInput?.focus());
        },

        isChoiceDisabled(choice) {
            return glueField.disabled || glueField.disabled_choices?.some(
                value => String(value) === String(choice.value)
            );
        },

        addChoice(choice) {
            if (!choice || this.isChoiceDisabled(choice)) return;
            glueField.addChoice(choice.value);
            this.search = '';
            glueField.clearSearch?.();
            this.dispatchValueEvents();
            this.$nextTick(() => this.$refs.searchInput?.focus());
        },

        close() {
            this.isOpen = false;
            this.search = '';
            glueField.clearSearch?.();
        },

        removeChoice(choice) {
            if (this.isChoiceDisabled(choice)) return;
            glueField.removeChoice(choice.value);
            this.dispatchValueEvents();
        },

        dispatchValueEvents() {
            this.$refs.trigger?.dispatchEvent(new Event('input', {bubbles: true}));
            this.$refs.trigger?.dispatchEvent(new Event('change', {bubbles: true}));
        },

        async searchChoices() {
            if (!glueField?.choices_searchable) return;
            await glueField.searchChoices(this.search.trim());
        }
    }));
});
