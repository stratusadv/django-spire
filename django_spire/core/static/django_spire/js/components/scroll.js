/**
 * The Alpine components behind django_spire/component/scroll/. Each is set on
 * an element inside a scroll component's own scope, so `this.component` is the
 * scroll's Glue component.
 *
 * scrollComponent({batchSize, rendersRows}) loads the list a batch at a time.
 * `rendersRows` says the server sends rows as markup; otherwise it sends them
 * as data and the template draws `items`.
 *
 * crudScrollComponent adds createItem(), editItem() and deleteItem(). It takes
 * the same options, and more for a list whose form or delete is a page:
 * `createUrl`, and `editUrl` and `deleteUrl`, each a function from a row's key
 * to its URL. A page link carries a `return_url`: `formReturnUrl` or
 * `deleteReturnUrl` when given, and otherwise the address the list is shown at.
 */
document.addEventListener('alpine:init', () => {
    const scrollComponent = ({batchSize, rendersRows}) => ({
        async init() {
            this.component.$on('item_added', event => this.addItem(this.eventKey(event)));
            this.component.$on('item_changed', event => this.refreshItem(this.eventKey(event)));
            this.component.$on('item_removed', event => this.removeItem(this.eventKey(event)));

            const generation = this.loadGeneration;

            this.isLoading = true;

            try {
                await this.showFirstBatch();
            }
            finally {
                if (generation === this.loadGeneration) {
                    this.isLoading = false;
                }
            }

            const scrollObserver = new IntersectionObserver(entries => {
                if (entries.some(entry => entry.isIntersecting)) {
                    this.loadMoreItems();
                }
            }, {threshold: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]});

            scrollObserver.observe(this.$refs.sentinel);
        },

        batchSize,
        glueBatches: [],
        hasMore: false,
        isLoading: false,
        items: [],
        keys: [],
        loadGeneration: 0,
        loadedCount: 0,
        rendersRows,

        async addItem(key) {
            if (this.rendersRows ? this.findRow(key) !== null : this.indexOfKey(key) !== -1) {
                await this.refreshItem(key);
                return;
            }

            const result = await this.component.load_item({key});

            if (result === null || result === undefined) {
                return;
            }

            if (this.rendersRows) {
                await result.renderInsertAdjacentHtmlAfterBegin(this.$refs.list);
            }
            else {
                const added = this.readItem(result);

                this.items.unshift(added.item);
                this.keys.unshift(added.key);
            }

            this.updateCount();
        },
        checkSentinel() {
            const sentinelCheck = new IntersectionObserver(entries => {
                sentinelCheck.disconnect();

                if (entries.some(entry => entry.isIntersecting)) {
                    this.loadMoreItems();
                }
            });

            sentinelCheck.observe(this.$refs.sentinel);
        },
        disposeAfterRender(items) {
            this.$nextTick(() => items.forEach(item => item.$dispose?.()));
        },
        eventKey(event) {
            const key = event.detail?.key;

            if (key === undefined || key === null) {
                throw new Error(`A scroll item event needs a key: fire it as self.${event.type}(key=...).`);
            }

            return key;
        },
        findRow(key) {
            return this.$refs.list.querySelector(`:scope > [data-scroll-key='${CSS.escape(String(key))}']`);
        },
        indexOfKey(key) {
            return this.keys.findIndex(existingKey => String(existingKey) === String(key));
        },
        async loadMoreItems() {
            if (this.isLoading || !this.hasMore) {
                return;
            }

            const generation = this.loadGeneration;

            this.isLoading = true;

            try {
                const result = await this.component.load_items({offset: this.loadedCount});

                if (generation !== this.loadGeneration) {
                    if (!this.rendersRows) {
                        result.$dispose?.();
                    }

                    return;
                }

                if (this.rendersRows) {
                    await result.renderInsertAdjacentHtmlBeforeEnd(this.$refs.list);
                    this.hasMore = this.renderedHasMore();
                }
                else {
                    const batch = this.readBatch(result);

                    this.items.push(...batch.items);
                    this.keys.push(...batch.keys);
                    this.hasMore = batch.hasMore;
                }

                this.updateCount();
            }
            finally {
                if (generation === this.loadGeneration) {
                    this.isLoading = false;
                }
            }

            this.checkSentinel();
        },
        readBatch(result) {
            if (typeof result.$dispose !== 'function') {
                return {items: [...result.items], keys: [...result.keys], hasMore: result.has_more};
            }

            const items = [...result.items];

            this.glueBatches.push(result);

            return {
                items,
                keys: items.map(item => item.$pk),
                hasMore: items.length === this.batchSize,
            };
        },
        readItem(result) {
            if (typeof result.$dispose !== 'function') {
                return {item: result.item, key: result.key};
            }

            return {item: result, key: result.$pk};
        },
        async refreshItem(key) {
            const result = await this.component.load_item({key});

            if (result === null || result === undefined) {
                this.removeItem(key);
                return;
            }

            if (this.rendersRows) {
                const row = this.findRow(key);

                if (row !== null) {
                    await result.renderOuterHtml(row);
                }

                return;
            }

            const index = this.indexOfKey(key);

            if (index !== -1) {
                const refreshed = this.readItem(result).item;
                const replaced = this.items[index];

                this.items[index] = refreshed;

                if (replaced !== refreshed) {
                    this.disposeAfterRender([replaced]);
                }
            }
        },
        async reloadItems() {
            const generation = ++this.loadGeneration;

            this.isLoading = true;

            try {
                await this.component.$refresh({submit: true});

                if (generation !== this.loadGeneration) {
                    return;
                }

                await this.showFirstBatch();
                this.checkSentinel();
            }
            finally {
                if (generation === this.loadGeneration) {
                    this.isLoading = false;
                }
            }
        },
        removeItem(key) {
            if (this.rendersRows) {
                this.findRow(key)?.remove();
            }
            else {
                const index = this.indexOfKey(key);

                if (index !== -1) {
                    this.disposeAfterRender(this.items.splice(index, 1));
                    this.keys.splice(index, 1);
                }
            }

            this.updateCount();
        },
        renderedHasMore() {
            const batchEnds = this.$refs.list.querySelectorAll(':scope > template[data-scroll-batch-end]');

            return batchEnds[batchEnds.length - 1]?.dataset.scrollHasMore === 'true';
        },
        async showFirstBatch() {
            if (this.rendersRows) {
                this.hasMore = this.renderedHasMore();
                this.updateCount();

                return;
            }

            const generation = this.loadGeneration;
            const result = this.component.first_batch_data
                ?? await this.component.load_items({offset: 0});

            if (generation !== this.loadGeneration) {
                result.$dispose?.();

                return;
            }

            const replaced = [...this.items, ...this.glueBatches];

            this.glueBatches = [];

            const firstBatch = this.readBatch(result);

            this.items = firstBatch.items;
            this.keys = firstBatch.keys;
            this.hasMore = firstBatch.hasMore;
            this.updateCount();
            this.disposeAfterRender(replaced);
        },
        updateCount() {
            this.loadedCount = this.rendersRows
                ? this.$refs.list.querySelectorAll(':scope > [data-scroll-key]').length
                : this.items.length;
        },
    });

    Alpine.data('scrollComponent', scrollComponent);

    Alpine.data('crudScrollComponent', ({
        createUrl = null,
        deleteReturnUrl = null,
        deleteUrl = null,
        editUrl = null,
        formReturnUrl = null,
        ...options
    }) => ({
        ...scrollComponent(options),

        async createItem() {
            if (createUrl !== null) {
                this.goToPage(createUrl, formReturnUrl);
                return;
            }

            const form = await this.component.load_item_form();

            form.model.form.$on('saved', ({detail}) => {
                this.addItem(detail.pk);
                Spire.modal.close();
            });
            await Spire.modal.dispatchGlueComponent(form);
        },
        async deleteItem(itemOrKey) {
            const key = this.resolveKey(itemOrKey);

            if (deleteUrl !== null) {
                this.goToPage(deleteUrl(key), deleteReturnUrl);
                return;
            }

            const confirmation = await this.component.load_item_delete_confirmation({pk: key});

            confirmation.$on('cancelled', () => Spire.modal.close());
            confirmation.$on('confirmed', ({detail}) => {
                this.removeItem(detail.pk);
                Spire.modal.close();
            });
            await Spire.modal.dispatchGlueComponent(confirmation);
        },
        async editItem(itemOrKey) {
            const key = this.resolveKey(itemOrKey);

            if (editUrl !== null) {
                this.goToPage(editUrl(key), formReturnUrl);
                return;
            }

            const form = await this.component.load_item_form({pk: key});

            form.model.form.$on('saved', ({detail}) => {
                this.refreshItem(detail.pk);
                Spire.modal.close();
            });
            await Spire.modal.dispatchGlueComponent(form);
        },
        goToPage(url, returnUrl) {
            const destination = returnUrl ?? `${window.location.pathname}${window.location.search}`;
            const separator = url.includes('?') ? '&' : '?';

            window.location.href = `${url}${separator}return_url=${encodeURIComponent(destination)}`;
        },
        resolveKey(itemOrKey) {
            if (itemOrKey === null || typeof itemOrKey !== 'object') {
                return itemOrKey;
            }

            const index = this.items.indexOf(itemOrKey);

            if (index === -1) {
                throw new Error('A scroll action was given an object that is not one of its items.');
            }

            return this.keys[index];
        },
    }));
});
