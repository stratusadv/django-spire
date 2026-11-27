document.addEventListener('alpine:init', () => {
    /**
     * A single-select dropdown over a choice source, rendered by
     * django_spire/widget/search_and_select_widget.html.
     *
     * A source has `choices` ([{value, label}]), `selectedChoice` and a `value`
     * that is read and set. It may also have `disabled`, `hasErrors`,
     * `choiceLabelHtml(choice)` and `choiceLabelText(choice)`, and, for choices
     * searched on the server, `choices_searchable`, `isSearchingChoices`,
     * `searchChoices(text)` and `clearSearch()`. A Glue form field is a source.
     */
    Alpine.data('searchAndSelect', (source, getActionChoices = () => []) => ({
        ...Spire.widget.dropdown,

        showDropdown: false,
        searchQuery: '',
        activeOptionClass: 'active',

        get isDropdownOpen() {
            return this.showDropdown;
        },

        onSearchInput() {
            if (!this.isSearchable) {
                this.resetActiveIndex(this.navigableChoices.length);
            }
        },

        get hasEmptyChoice() {
            return this.$root?.dataset?.includeEmpty === 'true' && this.searchQuery.length === 0;
        },

        get choiceCount() {
            return (this.hasEmptyChoice ? 1 : 0) + this.filteredChoices.length;
        },

        get actionChoices() {
            const items = typeof getActionChoices === 'function' ? getActionChoices() : [];
            return Array.isArray(items) ? items : [];
        },

        get navigableChoices() {
            const choices = this.hasEmptyChoice
                ? [{value: null}, ...this.filteredChoices]
                : [...this.filteredChoices];

            if (!this.actionChoices.length) {
                return choices;
            }

            return [
                ...choices,
                ...this.actionChoices.map(action => ({__actionChoice: action})),
            ];
        },

        get selectedChoice() {
            return source?.selectedChoice;
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

        labelHtml(choice) {
            return source?.choiceLabelHtml
                ? source.choiceLabelHtml(choice)
                : Spire.widget.escapeHtml(choice?.label ?? '');
        },

        labelText(choice) {
            if (!choice) return '';
            return source?.choiceLabelText ? source.choiceLabelText(choice) : String(choice.label ?? '');
        },

        syncActiveIndex() {
            const selectedValue = this.searchQuery.length === 0 ? this.selectedChoice?.value : undefined;
            const selectedIndex = selectedValue === undefined
                ? -1
                : this.navigableChoices.findIndex(
                    choice => !choice.__actionChoice && String(choice.value) === String(selectedValue)
                );
            this.resetActiveIndex(this.navigableChoices.length, selectedIndex);
        },

        openDropdown() {
            if (this.isDisabled) return;
            this.searchQuery = '';
            source.clearSearch?.();
            this.positionDropdown(this.$refs.selectedInput);
            this.showDropdown = true;
            this.syncActiveIndex();
            this.$nextTick(() => this.$refs.searchInput?.focus());
        },

        get filteredChoices() {
            if (this.isSearchable) {
                return this.isSearching ? [] : source?.choices || [];
            }

            const query = this.searchQuery.toLowerCase();

            return (source?.choices || []).filter(
                choice => String(choice.label).toLowerCase().includes(query)
                    || String(choice.value).toLowerCase().includes(query)
            );
        },

        closeDropdown() {
            this.showDropdown = false;
            this.searchQuery = '';
            this.activeIndex = -1;
            source.clearSearch?.();
        },

        async searchChoices() {
            if (!this.isSearchable) return;
            this.activeIndex = -1;
            await source.searchChoices(this.searchQuery.trim());
            if (this.activeIndex < 0) {
                this.syncActiveIndex();
            }
        },

        moveActive(delta) {
            this.moveHighlight(delta, this.navigableChoices.length);
        },

        selectActive() {
            const choice = this.navigableChoices[this.activeIndex];
            if (!choice) return;
            if (choice.__actionChoice) {
                this.runActionChoice(choice.__actionChoice);
                return;
            }
            this.selectItem(choice);
        },

        activateActive() {
            this.selectActive();
        },

        runActionChoice(actionChoice) {
            if (this.isDisabled || !actionChoice) return;
            const query = this.searchQuery;
            this.closeDropdown();
            actionChoice.onClick?.(query);
        },

        selectItem(choice) {
            if (this.isDisabled) return;
            source.value = choice.value;
            this.closeDropdown();
            this.$nextTick(() => this.dispatchValueEvents(this.$refs.selectedInput));
        }
    }));
});
