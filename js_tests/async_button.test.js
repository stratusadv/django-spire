import {afterEach, describe, expect, test} from 'bun:test'
import {deferred, mount, settle} from './utils'

afterEach(() => {
    document.body.innerHTML = ''
    delete window.work
})

function holdWork() {
    const held = []

    window.work = () => {
        const call = deferred()
        held.push(call)

        return call.promise
    }

    return held
}

describe('asyncButton', () => {
    test('runs one call for two clicks and is off until it settles', async () => {
        const held = holdWork()
        await mount(`<button id="save" x-bind="asyncButton(() => work())">Save</button>`)
        const button = document.getElementById('save')

        button.click()
        button.click()
        await settle()

        expect(held.length).toBe(1)
        expect(button.disabled).toBe(true)
        expect(Alpine.$data(button).isRunning).toBe(true)

        held[0].resolve()
        await settle()

        expect(button.disabled).toBe(false)
        expect(Alpine.$data(button).isRunning).toBe(false)

        button.click()
        await settle()

        expect(held.length).toBe(2)
    })

    test('comes back on after a call that fails', async () => {
        const held = holdWork()
        await mount(`<button id="save" x-bind="asyncButton(() => work().catch(() => {}))">Save</button>`)
        const button = document.getElementById('save')

        button.click()
        await settle()
        held[0].reject(new Error('the server said no'))
        await settle()

        expect(button.disabled).toBe(false)
        expect(Alpine.$data(button).isRunning).toBe(false)
    })

    test('buttons that name the same flag take turns', async () => {
        const held = holdWork()
        await mount(`
            <div id="group" x-data="{ isSettling: false }">
                <button id="cancel" x-bind="asyncButton(() => work(), 'isSettling')">Cancel</button>
                <button id="confirm" x-bind="asyncButton(() => work(), 'isSettling')">Confirm</button>
            </div>
        `)
        const cancel = document.getElementById('cancel')
        const confirm = document.getElementById('confirm')

        confirm.click()
        await settle()
        cancel.click()
        await settle()

        expect(held.length).toBe(1)
        expect(confirm.disabled).toBe(true)
        expect(cancel.disabled).toBe(true)
        expect(Alpine.$data(confirm).isRunning).toBe(true)
        expect(Alpine.$data(cancel).isRunning).toBe(false)
        expect(Alpine.$data(document.getElementById('group')).isSettling).toBe(true)

        held[0].resolve()
        await settle()

        expect(confirm.disabled).toBe(false)
        expect(cancel.disabled).toBe(false)
        expect(Alpine.$data(document.getElementById('group')).isSettling).toBe(false)
    })

    test('a button with no flag does not turn off its neighbour', async () => {
        const held = holdWork()
        await mount(`
            <div x-data>
                <button id="first" x-bind="asyncButton(() => work())">First</button>
                <button id="second" x-bind="asyncButton(() => work())">Second</button>
            </div>
        `)

        document.getElementById('first').click()
        await settle()

        expect(document.getElementById('first').disabled).toBe(true)
        expect(document.getElementById('second').disabled).toBe(false)

        document.getElementById('second').click()
        await settle()

        expect(held.length).toBe(2)
    })

    test('shows its state to markup inside the button', async () => {
        const held = holdWork()
        await mount(`
            <button id="save" x-bind="asyncButton(() => work())">
                <span id="spinner" x-show="isRunning"></span>Save
            </button>
        `)
        const spinner = document.getElementById('spinner')

        expect(spinner.style.display).toBe('none')

        document.getElementById('save').click()
        await settle()

        expect(spinner.style.display).not.toBe('none')

        held[0].resolve()
        await settle()

        expect(spinner.style.display).toBe('none')
    })

    test('works as a data component on an element that binds its button', async () => {
        const held = holdWork()
        await mount(`<button id="save" x-data="asyncButton(() => work())" x-bind="button">Save</button>`)
        const button = document.getElementById('save')

        button.click()
        button.click()
        await settle()

        expect(held.length).toBe(1)
        expect(button.disabled).toBe(true)

        held[0].resolve()
        await settle()

        expect(button.disabled).toBe(false)
    })
})
