document.addEventListener('alpine:init', () => {
    const escapeHtml = (text) => String(text)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');

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
    Alpine.data('searchAndSelect', (source) => ({
        ...Spire.widget.dropdownNavigation,

        showDropdown: false,
        searchQuery: '',
        openUp: false,
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

        get navigableChoices() {
            return this.hasEmptyChoice
                ? [{value: null}, ...this.filteredChoices]
                : this.filteredChoices;
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
            return source?.choiceLabelHtml ? source.choiceLabelHtml(choice) : escapeHtml(choice?.label ?? '');
        },

        labelText(choice) {
            if (!choice) return '';
            return source?.choiceLabelText ? source.choiceLabelText(choice) : String(choice.label ?? '');
        },

        getClippingRect() {
            let element = this.$refs.selectedInput.parentElement;

            while (element) {
                let style = window.getComputedStyle(element);
                let overflowY = style.overflowY;

                if (['auto', 'scroll', 'hidden'].includes(overflowY)) {
                    return element.getBoundingClientRect();
                }

                element = element.parentElement;
            }

            return {
                top: 0,
                bottom: window.innerHeight,
            };
        },

        openDropdown() {
            if (this.isDisabled) return;
            this.searchQuery = '';
            source.clearSearch?.();
            const rect = this.$refs.selectedInput.getBoundingClientRect();
            const clippingRect = this.getClippingRect();
            const spaceBelow = clippingRect.bottom - rect.bottom;
            const spaceAbove = rect.top - clippingRect.top;

            this.openUp = spaceBelow < 260 && spaceAbove > spaceBelow;
            this.showDropdown = true;
            const selectedValue = this.selectedChoice?.value;
            const selectedIndex = selectedValue === undefined
                ? -1
                : this.navigableChoices.findIndex(choice => String(choice.value) === String(selectedValue));
            this.resetActiveIndex(this.navigableChoices.length, selectedIndex);
            this.$nextTick(() => this.$refs.searchInput?.focus());
        },

        get dropdownStyle() {
            const verticalPosition = this.openUp ? 'bottom: 100%; margin-bottom: 0.25rem;' : 'top: 100%; margin-top: 0.25rem;';
            return `max-height: 250px; overflow-y: auto; z-index: 1070; ${verticalPosition}`;
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
            await source.searchChoices(this.searchQuery.trim());
            this.resetActiveIndex(this.navigableChoices.length);
        },

        moveActive(delta) {
            this.moveHighlight(delta, this.navigableChoices.length);
        },

        selectActive() {
            const choice = this.navigableChoices[this.activeIndex];
            if (choice) {
                this.selectItem(choice);
            }
        },

        activateActive() {
            this.selectActive();
        },

        selectItem(choice) {
            if (this.isDisabled) return;
            source.value = choice.value;
            this.closeDropdown();
            this.$nextTick(() => {
                this.$refs.selectedInput?.dispatchEvent(new Event('input', {bubbles: true}));
                this.$refs.selectedInput?.dispatchEvent(new Event('change', {bubbles: true}));
            });
        }
    }));
});
