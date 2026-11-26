Spire.widget = Spire.widget || {};

Spire.widget.escapeHtml = (text) => String(text)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');

/**
 * Shared active-option navigation and popover positioning for searchable
 * dropdown and combobox widgets.
 *
 * Mixed into Alpine components that expose a `$refs.dropdown` container whose
 * navigable options carry `[data-choice-item]`.
 */
Spire.widget.dropdown = {
    activeIndex: -1,
    openUp: false,

    init() {
        this.$watch(() => this.navigableChoices.length, () => {
            if (this.isDropdownOpen && this.activeIndex < 0) {
                this.syncActiveIndex();
            }
        });
    },

    get dropdownStyle() {
        const verticalPosition = this.openUp
            ? 'bottom: 100%; margin-bottom: 0.25rem;'
            : 'top: 100%; margin-top: 0.25rem;';
        return `max-height: 250px; overflow-y: auto; z-index: 1070; ${verticalPosition}`;
    },

    getClippingRect(anchor) {
        let element = anchor?.parentElement;

        while (element) {
            const overflowY = window.getComputedStyle(element).overflowY;
            if (['auto', 'scroll', 'hidden'].includes(overflowY)) {
                return element.getBoundingClientRect();
            }
            element = element.parentElement;
        }

        return {top: 0, bottom: window.innerHeight};
    },

    positionDropdown(anchor) {
        if (!anchor) return;
        const rect = anchor.getBoundingClientRect();
        const clippingRect = this.getClippingRect(anchor);
        const spaceBelow = clippingRect.bottom - rect.bottom;
        const spaceAbove = rect.top - clippingRect.top;

        this.openUp = spaceBelow < 260 && spaceAbove > spaceBelow;
    },

    dispatchValueEvents(element) {
        element?.dispatchEvent(new Event('input', {bubbles: true}));
        element?.dispatchEvent(new Event('change', {bubbles: true}));
    },

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

        '@keydown.enter'(event) {
            if (this.isDropdownOpen) {
                event.preventDefault();
                this.activateActive();
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
