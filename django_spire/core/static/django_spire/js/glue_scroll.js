document.addEventListener('alpine:init', () => {
    Alpine.data('glueScroll', (scrollQuerySet, orderBy, filterField) => ({
        searchQuery: '',
        orderBy: orderBy,
        filterField: filterField,
        scrollQuerySet: scrollQuerySet,
        pageQuerySet: null,
        items: [],
        isLoading: false,
        hasMore: true,
        loadGeneration: 0,

        init() {
            this.$watch('searchQuery', () => this.resetAndLoad());
            this.$watch('orderBy', () => this.resetAndLoad());

            window.addEventListener('updated-item', (event) => {
                if (!event.detail?.querysetName || event.detail.querysetName === this.scrollQuerySet._name) {
                    this.updateItem(event.detail.pk, event.detail.removed);
                }
            });

            const sentinelObserver = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting && this.hasMore) {
                        this.loadMoreItems();
                    }
                });
            }, { threshold: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] });

            if (this.$refs.scroll_sentinel) {
                sentinelObserver.observe(this.$refs.scroll_sentinel);
            }
        },

        async loadMoreItems() {
            if (this.isLoading || !this.hasMore) {
                return;
            }

            if (this.pageQuerySet === null) {
                await this.resetAndLoad();
                return;
            }

            const generation = this.loadGeneration;
            const pageQuerySet = this.pageQuerySet;
            this.isLoading = true;

            try {
                await pageQuerySet.loadMore();

                if (generation !== this.loadGeneration) {
                    return;
                }

                this.items = pageQuerySet.items;
                this.hasMore = pageQuerySet.hasNext;
            }
            finally {
                if (generation === this.loadGeneration) {
                    this.isLoading = false;
                }
            }
        },

        async resetAndLoad() {
            const generation = ++this.loadGeneration;

            this.isLoading = true;
            this.hasMore = true;
            this.items = [];

            let pageQuerySet = this.scrollQuerySet;

            if (this.filterField !== '') {
                pageQuerySet = pageQuerySet.filter({
                    [this.filterField + '__icontains']: this.searchQuery
                });
            }

            if (this.orderBy !== '') {
                pageQuerySet = pageQuerySet.orderBy(this.orderBy);
            }

            this.pageQuerySet = pageQuerySet;

            try {
                await pageQuerySet.refresh();

                if (generation !== this.loadGeneration) {
                    return;
                }

                this.items = pageQuerySet.items;
                this.hasMore = pageQuerySet.hasNext;
            }
            finally {
                if (generation === this.loadGeneration) {
                    this.isLoading = false;
                }
            }
        },

        async updateItem(pk, removed = false) {
            if (!pk) {
                return;
            }

            if (removed) {
                await this.resetAndLoad();
                return;
            }

            const item = await this.scrollQuerySet.get(pk);

            item.$collection = this.scrollQuerySet;
            const itemIndex = this.items.findIndex(existingItem => existingItem.$pk === item.$pk);

            if (itemIndex === -1) {
                this.items.unshift(item);
            }
            else {
                this.items[itemIndex] = item;
            }
        },

        toggleOrder() {
            this.orderBy = this.orderBy.startsWith('-') ? this.orderBy.slice(1) : '-' + this.orderBy;
        }
    }));
});
