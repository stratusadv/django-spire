document.addEventListener('alpine:init', () => {
    Alpine.data('searchAndSelect', (glueField, setValue) => ({
        showDropdown: false,
        searchQuery: '',
        openUp: false,

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
            this.searchQuery = '';
            glueField.clearSearch?.();
            const rect = this.$refs.selectedInput.getBoundingClientRect();
            const clippingRect = this.getClippingRect();
            const spaceBelow = clippingRect.bottom - rect.bottom;
            const spaceAbove = rect.top - clippingRect.top;

            this.openUp = spaceBelow < 260 && spaceAbove > spaceBelow;
            this.showDropdown = true;
            this.$nextTick(() => this.$refs.searchInput?.focus());
        },

        get dropdownStyle() {
            const verticalPosition = this.openUp ? 'bottom: 100%; margin-bottom: 0.25rem;' : 'top: 100%; margin-top: 0.25rem;';
            return `max-height: 250px; overflow-y: auto; z-index: 1070; ${verticalPosition}`;
        },

        get filteredChoices() {
            if (glueField?.choices_searchable) {
                return glueField.isSearchingChoices ? [] : glueField?.choices || [];
            }

            const query = this.searchQuery.toLowerCase();

            return (glueField?.choices || []).filter(
                choice => String(choice.label).toLowerCase().includes(query)
                    || String(choice.value).toLowerCase().includes(query)
            );
        },

        closeDropdown() {
            this.showDropdown = false;
            this.searchQuery = '';
            glueField.clearSearch?.();
        },

        async searchChoices() {
            if (!glueField?.choices_searchable) return;
            await glueField.searchChoices(this.searchQuery.trim());
        },

        selectItem(choice) {
            if (glueField.disabled) return;
            setValue(choice.value);
            this.closeDropdown();
            this.$nextTick(() => {
                this.$refs.selectedInput?.dispatchEvent(new Event('input', {bubbles: true}));
                this.$refs.selectedInput?.dispatchEvent(new Event('change', {bubbles: true}));
            });
        }
    }));
});
