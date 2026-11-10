document.addEventListener('alpine:init', () => {
    const escapeHtml = (text) => String(text)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');

    /**
     * A multi-select dropdown over a choice source, rendered by
     * django_spire/widget/multi_search_and_select_widget.html.
     *
     * A source has `choices` ([{value, label}]), `selectedChoices`,
     * `addChoice(value)` and `removeChoice(value)`. It may also have `disabled`,
     * `disabled_choices`, `hasErrors` and `choiceLabelHtml(choice)`, and, for
     * choices searched on the server, `choices_searchable`,
     * `isSearchingChoices`, `searchChoices(text)` and `clearSearch()`. A Glue
     * form field is a source; `Spire.widget.choiceSource()` builds one over any value.
     */
    Alpine.data('multiSearchAndSelect', (source) => ({
        isOpen: false,
        search: '',

        get selectedChoices() {
            return source?.selectedChoices || [];
        },

        get hasErrors() {
            return Boolean(source?.hasErrors);
        },

        get isDisabled() {
            return Boolean(source?.disabled);
        },

        get isSearchable() {
            return Boolean(source?.choices_searchable);
        },

        get isSearching() {
            return Boolean(source?.isSearchingChoices);
        },

        get filteredChoices() {
            if (this.isSearchable && this.isSearching) return [];

            const selectedValues = new Set(this.selectedChoices.map(choice => String(choice.value)));
            const query = this.search.trim().toLowerCase();
            return (source?.choices || []).filter(choice =>
                !selectedValues.has(String(choice.value))
                && (
                    this.isSearchable
                    || String(choice.label).toLowerCase().includes(query)
                )
            );
        },

        labelHtml(choice) {
            return source?.choiceLabelHtml ? source.choiceLabelHtml(choice) : escapeHtml(choice.label);
        },

        open() {
            if (this.isDisabled) return;
            this.search = '';
            source.clearSearch?.();
            this.isOpen = true;
            this.$nextTick(() => this.$refs.searchInput?.focus());
        },

        isChoiceDisabled(choice) {
            return this.isDisabled || Boolean(source.disabled_choices?.some(
                value => String(value) === String(choice.value)
            ));
        },

        addChoice(choice) {
            if (!choice || this.isChoiceDisabled(choice)) return;
            source.addChoice(choice.value);
            this.search = '';
            source.clearSearch?.();
            this.dispatchValueEvents();
            this.$nextTick(() => this.$refs.searchInput?.focus());
        },

        close() {
            this.isOpen = false;
            this.search = '';
            source.clearSearch?.();
        },

        removeChoice(choice) {
            if (this.isChoiceDisabled(choice)) return;
            source.removeChoice(choice.value);
            this.dispatchValueEvents();
        },

        dispatchValueEvents() {
            this.$refs.trigger?.dispatchEvent(new Event('input', {bubbles: true}));
            this.$refs.trigger?.dispatchEvent(new Event('change', {bubbles: true}));
        },

        async searchChoices() {
            if (!this.isSearchable) return;
            await source.searchChoices(this.search.trim());
        }
    }));
});
