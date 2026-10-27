import {afterEach, describe, expect, test} from 'bun:test'
import {deferred, mount, settle} from './utils'

afterEach(() => {
    document.body.innerHTML = ''
    delete window.component
})

function row(pk) {
    return {pk, name: `Row ${pk}`}
}

// Stands in for a scroll's Glue component: it serves rows from a list, a
// batch at a time, and records what the scroll asked it for.
function dataComponent(rows, batchSize = 2) {
    const listeners = {}
    const batch = offset => {
        const items = rows.slice(offset, offset + batchSize)

        return {items, keys: items.map(item => item.pk), has_more: rows.length > offset + batchSize}
    }

    return {
        calls: [],
        rows,
        get first_batch_data() {
            return batch(0)
        },
        $on(name, callback) {
            listeners[name] = callback
        },
        fire(name, detail) {
            return listeners[name]({type: name, detail})
        },
        async $refresh() {
            this.calls.push(['$refresh'])
        },
        async load_items({offset}) {
            this.calls.push(['load_items', offset])

            return batch(offset)
        },
        async load_item({key}) {
            this.calls.push(['load_item', key])
            const item = this.rows.find(candidate => String(candidate.pk) === String(key))

            return item ? {item, key: item.pk} : null
        },
    }
}

async function mountScroll(component, {name = 'scrollComponent', batchSize = 2} = {}) {
    window.component = component
    await mount(`
        <div x-data="{ component: window.component }">
            <div id="scroll" x-data="${name}({batchSize: ${batchSize}, rendersRows: false})">
                <div x-ref="list"></div>
                <div x-ref="sentinel"></div>
            </div>
        </div>
    `)

    return Alpine.$data(document.getElementById('scroll'))
}

describe('scrollComponent with data rows', () => {
    test('shows the first batch the component arrived with, without a request', async () => {
        const component = dataComponent([row(1), row(2), row(3)])

        const scroll = await mountScroll(component)

        expect(scroll.keys).toEqual([1, 2])
        expect(scroll.items.map(item => item.name)).toEqual(['Row 1', 'Row 2'])
        expect(scroll.loadedCount).toBe(2)
        expect(scroll.hasMore).toBe(true)
        expect(scroll.isLoading).toBe(false)
        expect(component.calls).toEqual([])
    })

    test('loads the next batch from the number of rows it holds', async () => {
        const component = dataComponent([row(1), row(2), row(3)])
        const scroll = await mountScroll(component)

        await scroll.loadMoreItems()

        expect(component.calls).toEqual([['load_items', 2]])
        expect(scroll.keys).toEqual([1, 2, 3])
        expect(scroll.hasMore).toBe(false)

        await scroll.loadMoreItems()

        expect(component.calls).toEqual([['load_items', 2]])
    })

    test('does not start a second load while one is in flight', async () => {
        const component = dataComponent([row(1), row(2), row(3)])
        const scroll = await mountScroll(component)
        const held = deferred()
        component.load_items = async ({offset}) => {
            component.calls.push(['load_items', offset])
            await held.promise

            return {items: [row(3)], keys: [3], has_more: false}
        }

        const first = scroll.loadMoreItems()
        const second = scroll.loadMoreItems()
        held.resolve()
        await Promise.all([first, second])

        expect(component.calls).toEqual([['load_items', 2]])
        expect(scroll.keys).toEqual([1, 2, 3])
    })

    test('a reload refreshes the component and shows the first batch again', async () => {
        const component = dataComponent([row(1), row(2), row(3)])
        const scroll = await mountScroll(component)
        await scroll.loadMoreItems()
        component.calls.length = 0
        component.rows.splice(0, 1)

        await scroll.reloadItems()

        expect(component.calls).toEqual([['$refresh']])
        expect(scroll.keys).toEqual([2, 3])
        expect(scroll.hasMore).toBe(false)
        expect(scroll.isLoading).toBe(false)
    })

    test('a batch that finishes after a newer reload began is never shown', async () => {
        const component = dataComponent([row(1), row(2), row(3), row(4), row(5)])
        const scroll = await mountScroll(component)
        const held = deferred()
        component.load_items = async () => {
            await held.promise

            return {items: [row(3), row(4)], keys: [3, 4], has_more: true}
        }

        const load = scroll.loadMoreItems()
        const reload = scroll.reloadItems()
        held.resolve()
        await Promise.all([load, reload])

        expect(scroll.keys).toEqual([1, 2])
        expect(scroll.loadedCount).toBe(2)
        expect(scroll.isLoading).toBe(false)
    })

    test('item_changed fetches that one row and replaces it in place', async () => {
        const component = dataComponent([row(1), row(2)])
        const scroll = await mountScroll(component)
        component.rows[1] = {pk: 2, name: 'Row 2 renamed'}

        await component.fire('item_changed', {key: 2})

        expect(component.calls).toEqual([['load_item', 2]])
        expect(scroll.items.map(item => item.name)).toEqual(['Row 1', 'Row 2 renamed'])
        expect(scroll.keys).toEqual([1, 2])
    })

    test('a changed row the component no longer has is removed', async () => {
        const component = dataComponent([row(1), row(2)])
        const scroll = await mountScroll(component)
        component.rows.splice(1, 1)

        await component.fire('item_changed', {key: 2})

        expect(scroll.keys).toEqual([1])
        expect(scroll.loadedCount).toBe(1)
    })

    test('item_added puts a new row at the top, and refreshes one already shown', async () => {
        const component = dataComponent([row(1), row(2)])
        const scroll = await mountScroll(component)
        component.rows.push(row(9))

        await component.fire('item_added', {key: 9})

        expect(scroll.keys).toEqual([9, 1, 2])
        expect(scroll.loadedCount).toBe(3)

        await component.fire('item_added', {key: 1})

        expect(scroll.keys).toEqual([9, 1, 2])
    })

    test('item_removed takes the row out without a request', async () => {
        const component = dataComponent([row(1), row(2)])
        const scroll = await mountScroll(component)

        await component.fire('item_removed', {key: 1})

        expect(scroll.keys).toEqual([2])
        expect(component.calls).toEqual([])
    })

    test('an item event without a key says how to fire it', async () => {
        const component = dataComponent([row(1)])
        await mountScroll(component)

        expect(() => component.fire('item_changed', {})).toThrow(
            'A scroll item event needs a key: fire it as self.item_changed(key=...).',
        )
    })
})

describe('scrollComponent with Glue rows', () => {
    function glueRow(pk, disposed) {
        return {
            $pk: pk,
            name: `Row ${pk}`,
            $dispose() {
                disposed.push(`row ${pk}`)
            },
        }
    }

    function glueComponent(pks, disposed) {
        const component = dataComponent([], 2)
        let batchNumber = 0

        Object.defineProperty(component, 'first_batch_data', {value: null})
        component.pks = pks
        component.load_items = async ({offset}) => {
            component.calls.push(['load_items', offset])
            const number = ++batchNumber

            return {
                items: component.pks.slice(offset, offset + 2).map(pk => glueRow(pk, disposed)),
                $dispose() {
                    disposed.push(`batch ${number}`)
                },
            }
        }

        return component
    }

    test('reads each key from the row and takes a full batch to mean there may be more', async () => {
        const component = glueComponent([1, 2, 3], [])

        const scroll = await mountScroll(component)

        expect(component.calls).toEqual([['load_items', 0]])
        expect(scroll.keys).toEqual([1, 2])
        expect(scroll.hasMore).toBe(true)

        await scroll.loadMoreItems()

        expect(scroll.keys).toEqual([1, 2, 3])
        expect(scroll.hasMore).toBe(false)
    })

    test('keeps each batch while its rows are shown and releases them all on a reload', async () => {
        const disposed = []
        const component = glueComponent([1, 2, 3], disposed)
        const scroll = await mountScroll(component)
        await scroll.loadMoreItems()

        expect(disposed).toEqual([])

        await scroll.reloadItems()
        await settle()

        expect(disposed.sort()).toEqual(['batch 1', 'batch 2', 'row 1', 'row 2', 'row 3'])
        expect(scroll.keys).toEqual([1, 2])
    })

    test('releases a single row that is removed', async () => {
        const disposed = []
        const component = glueComponent([1, 2], disposed)
        const scroll = await mountScroll(component)

        scroll.removeItem(1)
        await settle()

        expect(disposed).toEqual(['row 1'])
        expect(scroll.keys).toEqual([2])
    })
})

describe('crudScrollComponent', () => {
    function codedError(code) {
        return Object.assign(new Error(code), {code})
    }

    test('an action takes the item or its key', async () => {
        const scroll = await mountScroll(dataComponent([row(1), row(2)]), {name: 'crudScrollComponent'})

        expect(scroll.resolveKey(scroll.items[1])).toBe(2)
        expect(scroll.resolveKey(2)).toBe(2)
        expect(scroll.resolveKey('2')).toBe('2')
        expect(() => scroll.resolveKey({pk: 2})).toThrow(
            'A scroll action was given an object that is not one of its items.',
        )
    })

    test('a load that finds the row gone removes it and ends there', async () => {
        const scroll = await mountScroll(dataComponent([row(1), row(2)]), {name: 'crudScrollComponent'})

        const loaded = await scroll.loadForItem(1, async () => {
            throw codedError('model_instance_not_found')
        })

        expect(loaded).toBeNull()
        expect(scroll.keys).toEqual([2])
    })

    test('a load that fails any other way is passed on and leaves the row', async () => {
        const scroll = await mountScroll(dataComponent([row(1), row(2)]), {name: 'crudScrollComponent'})

        await expect(scroll.loadForItem(1, async () => {
            throw codedError('not_authorized')
        })).rejects.toThrow('not_authorized')
        expect(scroll.keys).toEqual([1, 2])
    })

    test('a load that succeeds returns what it loaded', async () => {
        const scroll = await mountScroll(dataComponent([row(1)]), {name: 'crudScrollComponent'})

        expect(await scroll.loadForItem(1, async () => 'the form')).toBe('the form')
        expect(scroll.keys).toEqual([1])
    })
})
