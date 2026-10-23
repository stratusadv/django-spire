window.Spire = window.Spire || {};

Spire.searchPalette = {
    open() {
        const url = window.django_spire?.search_palette?.url;

        if (url) {
            Spire.modal.dispatchView(url, {dialogClasses:'modal-lg'});
        }
    },
};

document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        Spire.searchPalette.open();
    }
});

document.addEventListener('alpine:init', () => {
    Alpine.data('searchPalette', () => ({
        query: '',
        timer: null,

        init() {
            this.resultsUrl = this.$el.dataset.resultsUrl || null;
            this.$el.closest('.modal')?.addEventListener(
                'shown.bs.modal',
                () => this.focusQuery(),
                {once: true}
            );
            this.focusQuery();
        },

        focusQuery() {
            this.$nextTick(() => this.$refs?.input?.focus());
        },

        onInput() {
            clearTimeout(this.timer);
            this.timer = setTimeout(() => this.fetchResults(), 150);
        },

        async fetchResults() {
            if (!this.resultsUrl) {
                return;
            }

            const url = new URL(this.resultsUrl, window.location.origin);
            url.searchParams.set('q', this.query);

            const response = await fetch(url, {
                headers: {'X-Requested-With': 'XMLHttpRequest'},
            });

            const html = await response.text();
            this.$refs.results.innerHTML = html;
            this.focusQuery();
        },

        focusNextResult(delta) {
            const results = Array.from(
                this.$refs.results.querySelectorAll('a.search-palette-result')
            );

            if (!results.length) {
                this.focusQuery();
                return;
            }

            const currentIndex = results.indexOf(document.activeElement);
            let nextIndex;

            if (currentIndex === -1) {
                nextIndex = delta > 0 ? 0 : results.length - 1;
            } else {
                nextIndex = currentIndex + delta;

                if (nextIndex < 0) {
                    this.focusQuery();
                    return;
                }

                if (nextIndex >= results.length) {
                    nextIndex = 0;
                }
            }

            results[nextIndex].focus();
        },

        activateFocusedResult() {
            const activeElement = document.activeElement;

            if (activeElement?.matches('a.search-palette-result')) {
                activeElement.click();
                return;
            }

            this.$refs.results.querySelector('a.search-palette-result')?.click();
        },

        refocusForTyping(event) {
            if (event.ctrlKey || event.metaKey || event.altKey || event.key.length !== 1) {
                return;
            }

            if (!document.activeElement?.matches('a.search-palette-result')) {
                return;
            }

            event.preventDefault();
            this.focusQuery();

            const input = this.$refs.input;
            input.value = this.query + event.key;
            input.dispatchEvent(new Event('input', {bubbles: true}));
        },
    }));
});
