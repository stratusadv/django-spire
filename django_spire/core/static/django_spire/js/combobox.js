document.addEventListener('alpine:init', () => {
    /**
     * A freeform text input with a filterable suggestion dropdown, rendered by
     * django_spire/widget/combobox_widget.html.
     *
     * A source has `value` (read and set) and may have `name`, `disabled`,
     * `required`, `hasErrors`, `max_length` and `min_length`. A Glue form field
     * is a source. Each suggestion returned by `getOptions()` is either a string
     * or `{value, label?, detail?, ...}`.
     */
    Alpine.data('combobox', (source, getOptions = () => [], onSelect = null) => ({
        ...Spire.widget.dropdown,

        showDropdown: false,
        activeOptionClass: 'active',
        _suppressNextInput: false,

        get isDropdownOpen() {
            return this.showDropdown;
        },

        get inputValue() {
            return source?.value ?? '';
        },

        set inputValue(nextValue) {
            if (source) {
                source.value = nextValue;
            }
        },

        get hasErrors() {
            return Boolean(source?.hasErrors);
        },

        get isDisabled() {
            return Boolean(source?.disabled);
        },

        get options() {
            const items = typeof getOptions === 'function' ? getOptions() : [];
            if (!Array.isArray(items)) return [];
            return items.map(item => (
                typeof item === 'object' && item !== null
                    ? {...item, value: item.value ?? item.label ?? '', label: item.label ?? item.value ?? ''}
                    : {value: String(item), label: String(item)}
            ));
        },

        get filteredOptions() {
            const query = String(source?.value ?? '').trim().toLowerCase();
            if (!query) return this.options;
            return this.options.filter(
                option => String(option.label).toLowerCase().includes(query)
                    || String(option.value).toLowerCase().includes(query)
            );
        },

        get navigableChoices() {
            return this.filteredOptions;
        },

        syncActiveIndex() {
            if (this.activeIndex >= this.navigableChoices.length) {
                this.activeIndex = -1;
            }
        },

        openDropdown() {
            if (this.isDisabled || !this.filteredOptions.length) return;
            this.positionDropdown(this.$refs.input);
            this.showDropdown = true;
            this.activeIndex = -1;
        },

        closeDropdown() {
            this.showDropdown = false;
            this.activeIndex = -1;
        },

        onInput(nextValue) {
            if (this._suppressNextInput) {
                this._suppressNextInput = false;
                return;
            }
            if (nextValue !== undefined && source) {
                source.value = nextValue;
            }
            this.activeIndex = -1;
            if (this.filteredOptions.length) {
                if (!this.showDropdown) {
                    this.openDropdown();
                }
            } else {
                this.closeDropdown();
            }
        },

        moveActive(delta) {
            if (!this.showDropdown) {
                this.openDropdown();
            }
            this.moveHighlight(delta, this.navigableChoices.length);
        },

        activateActive() {
            if (!this.showDropdown || this.activeIndex < 0) return false;
            const option = this.filteredOptions[this.activeIndex];
            if (!option) return false;
            this.selectOption(option);
            return true;
        },

        selectOption(option) {
            if (this.isDisabled || !option) return;
            source.value = option.value;
            if (this.$refs.input) {
                this.$refs.input.value = option.value;
            }
            this.closeDropdown();
            onSelect?.(option);
            this.$nextTick(() => {
                this._suppressNextInput = true;
                this.dispatchValueEvents(this.$refs.input);
            });
        },
    }));
});
