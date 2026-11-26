Spire.widget = Spire.widget || {};

/**
 * Shared active-option navigation for searchable dropdown widgets.
 *
 * Mixed into Alpine components that expose a `$refs.dropdown` container whose
 * navigable options carry `[data-choice-item]`.
 */
Spire.widget.dropdownNavigation = {
    activeIndex: -1,

    firstEnabledIndex(count, startIndex = 0, isDisabledAt = () => false) {
        for (let index = startIndex; index < count; index += 1) {
            if (!isDisabledAt(index)) return index;
        }
        return -1;
    },

    resetActiveIndex(count, preferredIndex = -1, isDisabledAt = () => false) {
        if (preferredIndex >= 0 && preferredIndex < count && !isDisabledAt(preferredIndex)) {
            this.activeIndex = preferredIndex;
            return;
        }
        this.activeIndex = this.firstEnabledIndex(count, 0, isDisabledAt);
    },

    moveHighlight(delta, count, isDisabledAt = () => false) {
        if (!count) {
            this.activeIndex = -1;
            return;
        }

        let next = this.activeIndex < 0
            ? (delta > 0 ? 0 : count - 1)
            : (this.activeIndex + delta + count) % count;

        for (let step = 0; step < count; step += 1) {
            if (!isDisabledAt(next)) {
                this.activeIndex = next;
                this.scrollActiveIntoView();
                return;
            }
            next = (next + delta + count) % count;
        }

        this.activeIndex = -1;
    },

    scrollActiveIntoView() {
        this.$nextTick(() => {
            const items = this.$refs.dropdown?.querySelectorAll('[data-choice-item]');
            items?.[this.activeIndex]?.scrollIntoView?.({block: 'nearest'});
        });
    },
};

document.addEventListener('alpine:init', () => {
    Alpine.bind('dropdownTrigger', () => ({
        ':class'() {
            return {'is-invalid': this.hasErrors};
        },

        ':disabled'() {
            return this.isDisabled;
        },

        '@keydown.arrow-down.prevent'() {
            if (this.isDropdownOpen) {
                this.moveActive(1);
            } else {
                this.openDropdown();
            }
        },

        '@keydown.arrow-up.prevent'() {
            if (this.isDropdownOpen) {
                this.moveActive(-1);
            } else {
                this.openDropdown();
            }
        },
    }));

    Alpine.bind('dropdownSearchInput', () => ({
        '@input.stop'() {
            queueMicrotask(() => this.onSearchInput());
        },

        '@input.stop.debounce.200ms'() {
            this.searchChoices();
        },

        '@change.stop'() {},

        '@keydown.arrow-down.prevent'() {
            this.moveActive(1);
        },

        '@keydown.arrow-up.prevent'() {
            this.moveActive(-1);
        },

        '@keydown.enter.prevent'() {
            this.activateActive();
        },

        '@keydown.escape.stop'() {
            this.closeDropdown();
        },
    }));

    Alpine.bind('dropdownOption', (getIndex) => ({
        'data-choice-item': '',
        role: 'option',

        ':class'() {
            return {[this.activeOptionClass]: this.activeIndex === getIndex()};
        },

        '@mouseenter'() {
            this.activeIndex = getIndex();
        },
    }));
});
