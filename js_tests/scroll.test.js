import {afterEach, describe, expect, test} from 'bun:test'
import {deferred, mount, settle} from './utils'

afterEach(() => {
    document.body.innerHTML = ''
    delete window.component
})

function row(pk) {
    return {pk, name: `Row ${pk}`}
}

// Stands in for a scroll's Glue component with Glue rows: it serves rows from
// a list, a batch at a time, as fresh Glue models, records what the scroll
// asked it for, and records which batches and rows the scroll released.
function glueComponent(rows, batchSize = 2) {
    const listeners = {}
    let batchNumber = 0

    const component = {
        calls: [],
        disposed: [],
        rows,
        glueRow({pk, name}) {
            return {
                $pk: pk,
                name,
                $dispose: () => component.disposed.push(`row ${pk}`),
            }
        },
        glueBatch(items) {
            const number = ++batchNumber

            return {
                items: items.map(item => component.glueRow(item)),
                $dispose: () => component.disposed.push(`batch ${number}`),
            }
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
        async load_glue_items({offset}) {
            this.calls.push(['load_glue_items', offset])

            return this.glueBatch(this.rows.slice(offset, offset + batchSize))
        },
        async load_glue_item({key}) {
            this.calls.push(['load_glue_item', key])
            const item = this.rows.find(candidate => String(candidate.pk) === String(key))

            return item ? this.glueRow(item) : null
        },
    }

    return component
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

describe('scrollComponent with Glue rows', () => {
    test('loads the first batch, reads each key from the row, and takes a full batch to mean there may be more', async () => {
        const component = glueComponent([row(1), row(2), row(3)])

        const scroll = await mountScroll(component)

        expect(component.calls).toEqual([['load_glue_items', 0]])
        expect(scroll.keys).toEqual([1, 2])
        expect(scroll.items.map(item => item.name)).toEqual(['Row 1', 'Row 2'])
        expect(scroll.loadedCount).toBe(2)
        expect(scroll.hasMore).toBe(true)
        expect(scroll.isLoading).toBe(false)
    })

    test('loads the next batch from the number of rows it holds', async () => {
        const component = glueComponent([row(1), row(2), row(3)])
        const scroll = await mountScroll(component)
        component.calls.length = 0

        await scroll.loadMoreItems()

        expect(component.calls).toEqual([['load_glue_items', 2]])
        expect(scroll.keys).toEqual([1, 2, 3])
        expect(scroll.hasMore).toBe(false)

        await scroll.loadMoreItems()

        expect(component.calls).toEqual([['load_glue_items', 2]])
    })

    test('does not start a second load while one is in flight', async () => {
        const component = glueComponent([row(1), row(2), row(3)])
        const scroll = await mountScroll(component)
        component.calls.length = 0
        const held = deferred()
        component.load_glue_items = async ({offset}) => {
            component.calls.push(['load_glue_items', offset])
            await held.promise

            return component.glueBatch([row(3)])
        }

        const first = scroll.loadMoreItems()
        const second = scroll.loadMoreItems()
        held.resolve()
        await Promise.all([first, second])

        expect(component.calls).toEqual([['load_glue_items', 2]])
        expect(scroll.keys).toEqual([1, 2, 3])
    })

    test('a reload refreshes the component and shows the first batch again', async () => {
        const component = glueComponent([row(1), row(2), row(3)])
        const scroll = await mountScroll(component)
        await scroll.loadMoreItems()
        component.calls.length = 0
        component.rows.splice(0, 1)

        await scroll.reloadItems()

        expect(component.calls).toEqual([['$refresh'], ['load_glue_items', 0]])
        expect(scroll.keys).toEqual([2, 3])
        expect(scroll.isLoading).toBe(false)
    })

    test('a batch that finishes after a newer reload began is never shown, and is released', async () => {
        const component = glueComponent([row(1), row(2), row(3), row(4), row(5)])
        const scroll = await mountScroll(component)
        const held = deferred()
        const heldBatch = component.glueBatch([row(3), row(4)])
        const loadItems = component.load_glue_items.bind(component)
        component.load_glue_items = async () => {
            component.load_glue_items = loadItems
            await held.promise

            return heldBatch
        }

        const load = scroll.loadMoreItems()
        const reload = scroll.reloadItems()
        held.resolve()
        await Promise.all([load, reload])

        expect(scroll.keys).toEqual([1, 2])
        expect(scroll.loadedCount).toBe(2)
        expect(scroll.isLoading).toBe(false)
        expect(component.disposed).toContain('batch 2')
    })

    test('item_changed fetches that one row and replaces it in place', async () => {
        const component = glueComponent([row(1), row(2)])
        const scroll = await mountScroll(component)
        component.calls.length = 0
        component.rows[1] = {pk: 2, name: 'Row 2 renamed'}

        await component.fire('item_changed', {key: 2})

        expect(component.calls).toEqual([['load_glue_item', 2]])
        expect(scroll.items.map(item => item.name)).toEqual(['Row 1', 'Row 2 renamed'])
        expect(scroll.keys).toEqual([1, 2])
    })

    test('a changed row the component no longer has is removed', async () => {
        const component = glueComponent([row(1), row(2)])
        const scroll = await mountScroll(component)
        component.rows.splice(1, 1)

        await component.fire('item_changed', {key: 2})

        expect(scroll.keys).toEqual([1])
        expect(scroll.loadedCount).toBe(1)
    })

    test('item_added puts a new row at the top, and refreshes one already shown', async () => {
        const component = glueComponent([row(1), row(2)])
        const scroll = await mountScroll(component)
        component.rows.push(row(9))

        await component.fire('item_added', {key: 9})

        expect(scroll.keys).toEqual([9, 1, 2])
        expect(scroll.loadedCount).toBe(3)

        await component.fire('item_added', {key: 1})

        expect(scroll.keys).toEqual([9, 1, 2])
    })

    test('item_removed takes the row out without a request', async () => {
        const component = glueComponent([row(1), row(2)])
        const scroll = await mountScroll(component)
        component.calls.length = 0

        await component.fire('item_removed', {key: 1})

        expect(scroll.keys).toEqual([2])
        expect(component.calls).toEqual([])
    })

    test('an item event without a key says how to fire it', async () => {
        const component = glueComponent([row(1)])
        await mountScroll(component)

        expect(() => component.fire('item_changed', {})).toThrow(
            'A scroll item event needs a key: fire it as self.item_changed(key=...).',
        )
    })

    test('keeps each batch while its rows are shown and releases them all on a reload', async () => {
        const component = glueComponent([row(1), row(2), row(3)])
        const scroll = await mountScroll(component)
        await scroll.loadMoreItems()

        expect(component.disposed).toEqual([])

        await scroll.reloadItems()
        await settle()

        expect(component.disposed.sort()).toEqual(['batch 1', 'batch 2', 'row 1', 'row 2', 'row 3'])
        expect(scroll.keys).toEqual([1, 2])
    })

    test('releases a single row that is removed', async () => {
        const component = glueComponent([row(1), row(2)])
        const scroll = await mountScroll(component)

        scroll.removeItem(1)
        await settle()

        expect(component.disposed).toEqual(['row 1'])
        expect(scroll.keys).toEqual([2])
    })

    test('releases a row that is replaced', async () => {
        const component = glueComponent([row(1), row(2)])
        const scroll = await mountScroll(component)

        await scroll.refreshItem(1)
        await settle()

        expect(component.disposed).toEqual(['row 1'])
        expect(scroll.keys).toEqual([1, 2])
    })
})

describe('crudScrollComponent', () => {
    function codedError(code) {
        return Object.assign(new Error(code), {code})
    }

    test('an action takes the item or its key', async () => {
        const scroll = await mountScroll(glueComponent([row(1), row(2)]), {name: 'crudScrollComponent'})

        expect(scroll.resolveKey(scroll.items[1])).toBe(2)
        expect(scroll.resolveKey(2)).toBe(2)
        expect(scroll.resolveKey('2')).toBe('2')
        expect(() => scroll.resolveKey({$pk: 2})).toThrow(
            'A scroll action was given an object that is not one of its items.',
        )
    })

    test('a load that finds the row gone removes it and ends there', async () => {
        const scroll = await mountScroll(glueComponent([row(1), row(2)]), {name: 'crudScrollComponent'})

        const loaded = await scroll.loadForItem(1, async () => {
            throw codedError('model_instance_not_found')
        })

        expect(loaded).toBeNull()
        expect(scroll.keys).toEqual([2])
    })

    test('a load that fails any other way is passed on and leaves the row', async () => {
        const scroll = await mountScroll(glueComponent([row(1), row(2)]), {name: 'crudScrollComponent'})

        await expect(scroll.loadForItem(1, async () => {
            throw codedError('not_authorized')
        })).rejects.toThrow('not_authorized')
        expect(scroll.keys).toEqual([1, 2])
    })

    test('a load that succeeds returns what it loaded', async () => {
        const scroll = await mountScroll(glueComponent([row(1)]), {name: 'crudScrollComponent'})

        expect(await scroll.loadForItem(1, async () => 'the form')).toBe('the form')
        expect(scroll.keys).toEqual([1])
    })
})
