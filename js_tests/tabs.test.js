import {afterEach, describe, expect, test} from 'bun:test'

import {settle} from './utils'


function mountTabs({activeTab = 'first', tabs = {}, urlParam = 'tab', initialLoaded = ['first'], loadTabImpl = null} = {}) {
    const events = new Map()
    const calls = []
    const component = {
        $on(name, callback) {
            if (!events.has(name)) {
                events.set(name, new Set())
            }
            events.get(name).add(callback)
        },
        emit(name, detail = {}) {
            for (const callback of events.get(name) || []) {
                callback({type: name, detail})
            }
        },
        async load_tab({tab_id}) {
            calls.push(tab_id)
            if (loadTabImpl) {
                return await loadTabImpl(tab_id)
            }
            return {
                async renderInnerHtml(pane) {
                    pane.innerHTML = `<div class="loaded-${tab_id}">Loaded ${tab_id} #${calls.length}</div>`
                },
            }
        },
    }

    const host = document.createElement('div')
    const config = JSON.stringify({activeTab, initialLoaded, tabs, urlParam})
    const buttonMarkup = Object.entries(tabs)
        .filter(([, meta]) => meta.kind !== 'link')
        .map(([id]) => `<button type="button" data-tab-id="${id}" @click="selectTab('${id}')">${id}</button>`)
        .join('')
    const paneMarkup = Object.entries(tabs)
        .filter(([, meta]) => meta.kind !== 'link')
        .map(([id]) => `<div data-tab-pane="${id}">${initialLoaded.includes(id) ? `Initial ${id}` : ''}</div>`)
        .join('')

    host.innerHTML = `<div x-data="tabsComponent()" data-tabs-config='${config}'><div>${buttonMarkup}</div>${paneMarkup}</div>`
    document.body.append(host)

    const root = host.firstElementChild
    Alpine.addScopeToNode(root, {component})
    Alpine.initTree(host)

    return {
        button: id => root.querySelector(`button[data-tab-id="${id}"]`),
        calls,
        component,
        data: () => Alpine.$data(root),
        host,
        pane: id => root.querySelector(`[data-tab-pane="${id}"]`),
        root,
    }
}


afterEach(() => {
    document.body.innerHTML = ''
    delete window.Glue
    window.history.replaceState(null, '', 'about:blank')
})


describe('spireTabs (static Bootstrap tabs)', () => {
    test('restores tab from query param and syncs URL on shown.bs.tab', async () => {
        window.history.replaceState(null, '', 'about:blank?tab=second')

        const clicked = []
        const host = document.createElement('div')
        host.innerHTML = `
            <ul x-data="spireTabs({urlParam: 'tab'})">
                <li><button class="nav-link active" data-bs-toggle="tab" data-tab-id="first">First</button></li>
                <li><button class="nav-link" data-bs-toggle="tab" data-tab-id="second">Second</button></li>
            </ul>
        `
        const secondButton = host.querySelector('[data-tab-id="second"]')
        secondButton.addEventListener('click', () => clicked.push('second'))
        document.body.append(host)

        Alpine.initTree(host)
        await settle()

        expect(clicked).toEqual(['second'])

        const firstButton = host.querySelector('[data-tab-id="first"]')
        firstButton.dispatchEvent(new CustomEvent('shown.bs.tab', {bubbles: true}))

        expect(new URL(window.location.href).searchParams.get('tab')).toBe('first')
    })
})


describe('tabsComponent', () => {
    test('loads lazily on first visit, caches when cache=true, and updates URL param', async () => {
        const {button, calls, pane} = mountTabs({
            activeTab: 'first',
            initialLoaded: ['first'],
            tabs: {
                first: {cache: true, kind: 'component', viewMethod: 'GET', viewUrl: null},
                second: {cache: true, kind: 'component', viewMethod: 'GET', viewUrl: null},
            },
            urlParam: 'tab',
        })
        await settle()

        expect(calls).toEqual([])

        // Click the descendant button so Alpine binds $el to the button rather than $root.
        button('second').click()
        await settle()
        expect(calls).toEqual(['second'])
        expect(pane('second').textContent).toBe('Loaded second #1')
        expect(new URL(window.location.href).searchParams.get('tab')).toBe('second')

        button('first').click()
        await settle()
        button('second').click()
        await settle()
        expect(calls).toEqual(['second'])
    })

    test('disposes and re-fetches uncached tabs on every visit', async () => {
        const disposed = []
        window.Glue = {
            from(node) {
                return {$dispose: () => disposed.push(node.getAttribute('data-glue-address'))}
            },
        }

        const {calls, data, pane} = mountTabs({
            activeTab: 'first',
            initialLoaded: ['first'],
            tabs: {
                first: {cache: false, kind: 'component', viewMethod: 'GET', viewUrl: null},
                second: {cache: false, kind: 'component', viewMethod: 'GET', viewUrl: null},
            },
            loadTabImpl: async tabId => ({
                async renderInnerHtml(target) {
                    target.innerHTML = `<div data-glue-address="addr:${tabId}:${calls.length}">Tab ${tabId}</div>`
                },
            }),
        })
        await settle()
        pane('first').innerHTML = '<div data-glue-address="addr:first:0">Initial</div>'

        await data().selectTab('second')
        expect(disposed).toEqual(['addr:first:0'])
        expect(calls).toEqual(['second'])

        await data().selectTab('first')
        expect(disposed).toEqual(['addr:first:0', 'addr:second:1'])
        expect(calls).toEqual(['second', 'first'])
    })

    test('invalidateTab marks hidden tabs stale without fetching and reloads active tab immediately', async () => {
        const {calls, component, data, pane} = mountTabs({
            activeTab: 'first',
            initialLoaded: ['first'],
            tabs: {
                first: {cache: true, kind: 'component', viewMethod: 'GET', viewUrl: null},
                second: {cache: true, kind: 'component', viewMethod: 'GET', viewUrl: null},
            },
        })
        await settle()

        await data().selectTab('second')
        await data().selectTab('first')
        expect(calls).toEqual(['second'])

        // Invalidate hidden tab via Glue event: zero immediate fetch.
        component.emit('tab_invalidated', {tab_id: 'second'})
        await settle()
        expect(calls).toEqual(['second'])
        expect(pane('second').innerHTML).toBe('')

        // Switching to the invalidated tab re-fetches it.
        await data().selectTab('second')
        expect(calls).toEqual(['second', 'second'])

        // Invalidating the currently active tab reloads it right away.
        component.emit('tab_invalidated', {tab_id: 'second'})
        await settle()
        expect(calls).toEqual(['second', 'second', 'second'])
    })

    test('reloadTab forces refresh of a cached tab', async () => {
        const {calls, data, pane} = mountTabs({
            activeTab: 'first',
            initialLoaded: ['first'],
            tabs: {
                first: {cache: true, kind: 'component', viewMethod: 'GET', viewUrl: null},
            },
        })
        await settle()

        await data().reloadTab('first')
        expect(calls).toEqual(['first'])
        expect(pane('first').textContent).toBe('Loaded first #1')
    })

    test('loads view tabs via Glue.view on init or switch', async () => {
        const fetched = []
        window.Glue = {
            registerComponentsFromDom() {},
            view(url) {
                return {
                    async get() {
                        fetched.push(`GET ${url}`)
                        return `<p>From GET ${url}</p>`
                    },
                    async renderInnerHtml(target) {
                        fetched.push(`POST ${url}`)
                        target.innerHTML = `<p>From POST ${url}</p>`
                    },
                }
            },
        }

        const {data, pane} = mountTabs({
            activeTab: 'get_view',
            initialLoaded: [],
            tabs: {
                get_view: {cache: true, kind: 'view', viewMethod: 'GET', viewUrl: '/tabs/a/'},
                post_view: {cache: true, kind: 'view', viewMethod: 'POST', viewUrl: '/tabs/b/'},
            },
        })
        await settle()

        expect(fetched).toEqual(['GET /tabs/a/'])
        expect(pane('get_view').innerHTML).toBe('<p>From GET /tabs/a/</p>')

        await data().selectTab('post_view')
        expect(fetched).toEqual(['GET /tabs/a/', 'POST /tabs/b/'])
        expect(pane('post_view').innerHTML).toBe('<p>From POST /tabs/b/</p>')
    })
})
