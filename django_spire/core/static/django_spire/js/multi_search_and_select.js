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
        ...Spire.widget.dropdownNavigation,

        isOpen: false,
        search: '',
        hasNavigated: false,
        activeOptionClass: 'active text-bg-primary',

        get isDropdownOpen() {
            return this.isOpen;
        },

        onSearchInput() {
            this.hasNavigated = false;
            if (!this.isSearchable) {
                this.resetForSearch();
            }
        },

        get selectedChoices() {
            return source?.selectedChoices || [];
        },

        get navigableChoices() {
            return [...this.selectedChoices, ...this.filteredChoices];
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

        syncActiveIndex() {
            this.resetForSearch();
        },

        open() {
            if (this.isDisabled) return;
            this.search = '';
            this.hasNavigated = false;
            source.clearSearch?.();
            this.isOpen = true;
            this.syncActiveIndex();
            this.$nextTick(() => this.$refs.searchInput?.focus());
        },

        isChoiceDisabled(choice) {
            return this.isDisabled || Boolean(source.disabled_choices?.some(
                value => String(value) === String(choice.value)
            ));
        },

        isChoiceDisabledAt(index) {
            const choice = this.navigableChoices[index];
            return !choice || this.isChoiceDisabled(choice);
        },

        resetForSearch() {
            const start = this.search.length > 0 ? this.selectedChoices.length : 0;
            const preferred = this.firstEnabledIndex(
                this.navigableChoices.length,
                start,
                (index) => this.isChoiceDisabledAt(index)
            );
            this.resetActiveIndex(this.navigableChoices.length, preferred, (index) => this.isChoiceDisabledAt(index));
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
            this.activeIndex = -1;
            this.hasNavigated = false;
            source.clearSearch?.();
        },

        removeChoice(choice) {
            if (this.isChoiceDisabled(choice)) return;
            source.removeChoice(choice.value);
            this.dispatchValueEvents();
        },

        moveActive(delta) {
            this.hasNavigated = true;
            this.moveHighlight(delta, this.navigableChoices.length, (index) => this.isChoiceDisabledAt(index));
        },

        toggleActive() {
            const choice = this.navigableChoices[this.activeIndex];
            if (!choice || this.isChoiceDisabled(choice)) return;

            const isSelected = this.activeIndex < this.selectedChoices.length;
            const toggledValue = String(choice.value);

            if (isSelected) {
                this.removeChoice(choice);
            } else {
                this.addChoice(choice);
            }

            this.hasNavigated = true;
            const updatedIndex = this.navigableChoices.findIndex(
                item => String(item.value) === toggledValue
            );
            const fallbackIndex = Math.min(this.activeIndex, this.navigableChoices.length - 1);
            this.resetActiveIndex(
                this.navigableChoices.length,
                updatedIndex >= 0 ? updatedIndex : fallbackIndex,
                (index) => this.isChoiceDisabledAt(index)
            );
            this.scrollActiveIntoView();
        },

        openDropdown() {
            this.open();
        },

        closeDropdown() {
            this.close();
        },

        activateActive() {
            this.toggleActive();
        },

        handleSpaceKey(event) {
            if (!this.hasNavigated && this.search.length > 0) return;
            event.preventDefault();
            this.toggleActive();
        },

        dispatchValueEvents() {
            this.$refs.trigger?.dispatchEvent(new Event('input', {bubbles: true}));
            this.$refs.trigger?.dispatchEvent(new Event('change', {bubbles: true}));
        },

        async searchChoices() {
            if (!this.isSearchable) return;
            this.activeIndex = -1;
            await source.searchChoices(this.search.trim());
            if (this.activeIndex < 0) {
                this.syncActiveIndex();
            }
        }
    }));
});
