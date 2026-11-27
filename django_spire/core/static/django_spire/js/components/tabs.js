/**
 * Alpine components for Spire's tabs:
 *
 * - `spireTabs({urlParam})` enhances static Bootstrap tabs
 *   (`django_spire/tab/section.html`) with optional URL query parameter
 *   syncing (`replaceState`) and initial tab restoration on load.
 *
 * - `tabsComponent()` drives `TabsComponent`
 *   (`django_spire/component/tab/tabs.html`), lazily loading component,
 *   template, or view tabs into per-tab panes with optional caching,
 *   URL query syncing, `invalidateTab()`, `reloadTab()`, and the
 *   `tab_invalidated` Glue event.
 */
document.addEventListener('alpine:init', () => {
    const syncUrlParam = (urlParam, tabId) => {
        if (!urlParam || !tabId) {
            return;
        }

        const url = new URL(window.location.href);

        if (url.searchParams.get(urlParam) === String(tabId)) {
            return;
        }

        url.searchParams.set(urlParam, String(tabId));
        window.history.replaceState(null, '', url);
    };

    Alpine.data('spireTabs', ({urlParam = ''} = {}) => ({
        init() {
            if (!this.urlParam) {
                return;
            }

            const requestedTabId = new URLSearchParams(window.location.search).get(this.urlParam);

            if (requestedTabId) {
                const button = this.$el.querySelector(
                    `[data-bs-toggle="tab"][data-tab-id="${CSS.escape(requestedTabId)}"]`,
                );

                if (button && !button.classList.contains('active')) {
                    if (window.bootstrap?.Tab) {
                        window.bootstrap.Tab.getOrCreateInstance(button).show();
                    } else {
                        button.click();
                    }
                }
            }

            this.$el.addEventListener('shown.bs.tab', event => {
                const tabId = event.target?.dataset?.tabId;
                if (tabId) {
                    syncUrlParam(this.urlParam, tabId);
                }
            });
        },

        urlParam,
    }));

    Alpine.data('tabsComponent', () => ({
        async init() {
            const root = this.$root || this.$el;
            const rawConfig = root?.dataset?.tabsConfig;
            const config = rawConfig ? JSON.parse(rawConfig) : {};

            this.tabs = config.tabs || {};
            this.activeTab = config.activeTab ?? null;
            this.urlParam = config.urlParam ?? null;
            this.loadedTabs = {};

            for (const tabId of config.initialLoaded || []) {
                this.loadedTabs[tabId] = true;
            }

            this.component?.$on?.('tab_invalidated', ({detail}) => {
                this.invalidateTab(detail?.tab_id ?? null);
            });

            if (this.activeTab && !this.loadedTabs[this.activeTab] && this.tabs[this.activeTab]?.kind === 'view') {
                await this.loadTab(this.activeTab);
            }
        },

        activeTab: null,
        loadGeneration: 0,
        loadedTabs: {},
        loadingTab: null,
        tabs: {},
        urlParam: null,

        disposePane(pane) {
            if (!pane) {
                return;
            }

            for (const node of pane.querySelectorAll('[data-glue-address]')) {
                const proxy = window.Glue?.from?.(node);

                if (proxy && proxy._record?.owner?.path == null) {
                    proxy.$dispose?.();
                }
            }

            pane.innerHTML = '';
        },

        async invalidateTab(tabId = null) {
            if (tabId === null || tabId === undefined) {
                const currentTab = this.activeTab;

                if (this.loadingTab !== null) {
                    ++this.loadGeneration;
                    this.loadingTab = null;
                }

                for (const id of Object.keys(this.tabs)) {
                    delete this.loadedTabs[id];

                    if (id !== currentTab) {
                        this.disposePane(this.paneFor(id));
                    }
                }

                if (currentTab && this.tabs[currentTab] && this.tabs[currentTab].kind !== 'link') {
                    await this.loadTab(currentTab);
                }

                return;
            }

            delete this.loadedTabs[tabId];

            if (this.loadingTab === tabId) {
                ++this.loadGeneration;
                this.loadingTab = null;
            }

            if (this.activeTab === tabId) {
                await this.loadTab(tabId);
            } else {
                this.disposePane(this.paneFor(tabId));
            }
        },

        isLoading(tabId = this.activeTab) {
            return this.loadingTab !== null && this.loadingTab === tabId;
        },

        async loadTab(tabId) {
            const tab = this.tabs[tabId];
            const pane = this.paneFor(tabId);

            if (!tab || tab.kind === 'link' || !pane) {
                return;
            }

            const generation = ++this.loadGeneration;
            this.loadingTab = tabId;

            try {
                if (tab.kind === 'view') {
                    const view = window.Glue.view(tab.viewUrl);
                    const html = tab.viewMethod === 'POST' ? await view.post() : await view.get();

                    if (generation !== this.loadGeneration) {
                        return;
                    }

                    this.disposePane(pane);

                    if (typeof html === 'string') {
                        pane.innerHTML = html;
                        window.Glue?.registerComponentsFromDom?.(pane);
                    }
                } else {
                    const result = await this.component.load_tab({tab_id: tabId});

                    if (generation !== this.loadGeneration) {
                        return;
                    }

                    if (result) {
                        await result.renderInnerHtml(pane);
                    } else {
                        this.disposePane(pane);
                    }
                }

                if (generation === this.loadGeneration) {
                    this.loadedTabs[tabId] = true;
                }
            } finally {
                if (generation === this.loadGeneration) {
                    this.loadingTab = null;
                }
            }
        },

        paneFor(tabId) {
            const root = this.$root || this.$el;
            return root?.querySelector(`[data-tab-pane="${CSS.escape(String(tabId))}"]`) ?? null;
        },

        async reloadTab(tabId = this.activeTab) {
            if (!tabId || !this.tabs[tabId] || this.tabs[tabId].kind === 'link') {
                return;
            }

            delete this.loadedTabs[tabId];

            if (this.activeTab === tabId) {
                await this.loadTab(tabId);
            } else {
                await this.selectTab(tabId, {force: true});
            }
        },

        async selectTab(tabId, {force = false} = {}) {
            const tab = this.tabs[tabId];

            if (!tab || tab.kind === 'link') {
                return;
            }

            const previousTab = this.activeTab;

            if (previousTab !== tabId && this.loadingTab !== null) {
                ++this.loadGeneration;
                this.loadingTab = null;
            }

            this.activeTab = tabId;
            syncUrlParam(this.urlParam, tabId);

            if (previousTab && previousTab !== tabId && !this.tabs[previousTab]?.cache) {
                delete this.loadedTabs[previousTab];
                this.disposePane(this.paneFor(previousTab));
            }

            if (force || !tab.cache || !this.loadedTabs[tabId]) {
                await this.loadTab(tabId);
            }
        },
    }));
});
