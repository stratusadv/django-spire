import {afterEach, describe, expect, test} from 'bun:test'

import {mount, settle} from './utils.js'

afterEach(() => {
    document.body.innerHTML = ''
    delete window.__testSource
})

function makeSingleSource(choices, {value = null, searchable = false} = {}) {
    return {
        choices,
        value,
        choices_searchable: searchable,
        isSearchingChoices: false,
        get selectedChoice() {
            return this.choices.find(choice => String(choice.value) === String(this.value)) || null
        },
        async searchChoices(query) {
            this.choices = choices.filter(choice =>
                choice.label.toLowerCase().includes(query.toLowerCase())
            )
        },
        clearSearch() {},
    }
}

function makeMultiSource(choices, {selected = [], disabled = [], searchable = false} = {}) {
    let current = [...selected]
    return {
        choices,
        disabled_choices: disabled,
        choices_searchable: searchable,
        isSearchingChoices: false,
        get selectedChoices() {
            const set = new Set(current.map(String))
            return this.choices.filter(choice => set.has(String(choice.value)))
        },
        addChoice(value) {
            if (!current.map(String).includes(String(value))) {
                current = [...current, value]
            }
        },
        removeChoice(value) {
            current = current.filter(existing => String(existing) !== String(value))
        },
        async searchChoices(query) {
            this.choices = choices.filter(choice =>
                choice.label.toLowerCase().includes(query.toLowerCase())
            )
        },
        clearSearch() {},
    }
}

function singleSelectHtml({includeEmpty = false} = {}) {
    return `
        <div
            id="root"
            ${includeEmpty ? 'data-include-empty="true"' : ''}
            x-data="searchAndSelect(window.__testSource)"
        >
            <input
                x-ref="selectedInput"
                type="text"
                x-bind="dropdownTrigger"
                @focus="openDropdown()"
                @click="openDropdown()"
                readonly
            >
            <div x-ref="dropdown" role="listbox" x-show="showDropdown">
                <input
                    x-ref="searchInput"
                    type="text"
                    x-model="searchQuery"
                    x-bind="dropdownSearchInput"
                >
                ${includeEmpty ? `
                    <template x-if="hasEmptyChoice">
                        <div x-bind="dropdownOption(() => 0)" @click="selectItem({value: null})">
                            Select ...
                        </div>
                    </template>
                ` : ''}
                <template x-for="(choice, index) in filteredChoices" :key="choice.value">
                    <div
                        x-bind="dropdownOption(() => hasEmptyChoice ? index + 1 : index)"
                        @click="selectItem(choice)"
                        x-text="choice.label"
                    ></div>
                </template>
            </div>
        </div>
    `
}

function multiSelectHtml() {
    return `
        <div id="root" x-data="multiSearchAndSelect(window.__testSource)">
            <button
                x-ref="trigger"
                type="button"
                x-bind="dropdownTrigger"
                @click="isOpen ? close() : open()"
            ></button>
            <div x-show="isOpen">
                <input
                    x-ref="searchInput"
                    type="search"
                    x-model="search"
                    x-bind="dropdownSearchInput"
                    @keydown.space="handleSpaceKey($event)"
                >
                <div x-ref="dropdown" role="listbox">
                    <template x-for="(choice, index) in selectedChoices" :key="'selected-' + choice.value">
                        <button
                            x-bind="dropdownOption(() => index)"
                            type="button"
                            :disabled="isChoiceDisabled(choice)"
                            @click="removeChoice(choice)"
                            x-text="choice.label"
                        ></button>
                    </template>
                    <template x-for="(choice, index) in filteredChoices" :key="choice.value">
                        <button
                            x-bind="dropdownOption(() => selectedChoices.length + index)"
                            type="button"
                            :disabled="isChoiceDisabled(choice)"
                            @click="addChoice(choice)"
                            x-text="choice.label"
                        ></button>
                    </template>
                </div>
            </div>
        </div>
    `
}

function pressKey(element, key) {
    const event = new KeyboardEvent('keydown', {key, bubbles: true, cancelable: true})
    element.dispatchEvent(event)
    return event
}

describe('searchAndSelect keyboard navigation', () => {
    test('arrows wrap through choices and Enter selects the highlighted choice', async () => {
        window.__testSource = makeSingleSource([
            {value: 'a', label: 'Alpha'},
            {value: 'b', label: 'Beta'},
            {value: 'c', label: 'Gamma'},
        ])
        await mount(singleSelectHtml())

        const data = Alpine.$data(document.getElementById('root'))
        const searchInput = document.querySelector('[x-ref="searchInput"]')

        data.openDropdown()
        await settle()
        expect(data.activeIndex).toBe(0)

        pressKey(searchInput, 'ArrowDown')
        expect(data.activeIndex).toBe(1)

        pressKey(searchInput, 'ArrowDown')
        expect(data.activeIndex).toBe(2)

        pressKey(searchInput, 'ArrowDown')
        expect(data.activeIndex).toBe(0)

        pressKey(searchInput, 'ArrowUp')
        expect(data.activeIndex).toBe(2)

        pressKey(searchInput, 'Enter')
        await settle()
        expect(window.__testSource.value).toBe('c')
        expect(data.showDropdown).toBe(false)
        expect(data.activeIndex).toBe(-1)
    })

    test('include_empty option is navigable when search is empty and clears the value', async () => {
        window.__testSource = makeSingleSource(
            [
                {value: 'a', label: 'Alpha'},
                {value: 'b', label: 'Beta'},
            ],
            {value: 'b'}
        )
        await mount(singleSelectHtml({includeEmpty: true}))

        const data = Alpine.$data(document.getElementById('root'))
        const searchInput = document.querySelector('[x-ref="searchInput"]')

        data.openDropdown()
        await settle()
        expect(data.activeIndex).toBe(2)

        pressKey(searchInput, 'ArrowDown')
        expect(data.activeIndex).toBe(0)

        pressKey(searchInput, 'Enter')
        await settle()
        expect(window.__testSource.value).toBeNull()
        expect(data.showDropdown).toBe(false)
    })

    test('local search resets highlight to the first matching choice', async () => {
        window.__testSource = makeSingleSource([
            {value: 'a', label: 'Alpha'},
            {value: 'b', label: 'Beta'},
            {value: 'c', label: 'Gamma'},
        ])
        await mount(singleSelectHtml())

        const data = Alpine.$data(document.getElementById('root'))
        const searchInput = document.querySelector('[x-ref="searchInput"]')

        data.openDropdown()
        await settle()
        pressKey(searchInput, 'ArrowDown')
        pressKey(searchInput, 'ArrowDown')
        expect(data.activeIndex).toBe(2)

        searchInput.value = 'bet'
        searchInput.dispatchEvent(new Event('input', {bubbles: true}))
        await settle()
        expect(data.activeIndex).toBe(0)

        pressKey(searchInput, 'Enter')
        expect(window.__testSource.value).toBe('b')
    })
})

describe('multiSearchAndSelect keyboard navigation', () => {
    test('arrows skip disabled choices and Space toggles a choice on and back off', async () => {
        window.__testSource = makeMultiSource(
            [
                {value: '1', label: 'Alpha'},
                {value: '2', label: 'Blocked'},
                {value: '3', label: 'Gamma'},
            ],
            {disabled: ['2']}
        )
        await mount(multiSelectHtml())

        const data = Alpine.$data(document.getElementById('root'))
        const searchInput = document.querySelector('[x-ref="searchInput"]')

        data.open()
        await settle()
        expect(data.activeIndex).toBe(0)

        pressKey(searchInput, 'ArrowDown')
        expect(data.activeIndex).toBe(2)

        const onEvent = pressKey(searchInput, ' ')
        await settle()
        expect(onEvent.defaultPrevented).toBe(true)
        expect(window.__testSource.selectedChoices.map(choice => choice.value)).toEqual(['3'])
        expect(data.isOpen).toBe(true)
        expect(data.activeIndex).toBe(0)

        const offEvent = pressKey(searchInput, ' ')
        await settle()
        expect(offEvent.defaultPrevented).toBe(true)
        expect(window.__testSource.selectedChoices).toEqual([])
        expect(data.activeIndex).toBe(2)
    })

    test('Space types normally while searching, and toggles after arrow navigation', async () => {
        window.__testSource = makeMultiSource(
            [
                {value: '1', label: 'Alpha'},
                {value: '2', label: 'High Priority'},
                {value: '3', label: 'High Impact'},
            ],
            {selected: ['1']}
        )
        await mount(multiSelectHtml())

        const data = Alpine.$data(document.getElementById('root'))
        const searchInput = document.querySelector('[x-ref="searchInput"]')

        data.open()
        await settle()

        searchInput.value = 'High'
        searchInput.dispatchEvent(new Event('input', {bubbles: true}))
        await settle()
        expect(data.activeIndex).toBe(1)

        const typingSpace = pressKey(searchInput, ' ')
        expect(typingSpace.defaultPrevented).toBe(false)

        pressKey(searchInput, 'ArrowDown')
        expect(data.activeIndex).toBe(2)

        const toggleSpace = pressKey(searchInput, ' ')
        await settle()
        expect(toggleSpace.defaultPrevented).toBe(true)
        expect(window.__testSource.selectedChoices.map(choice => choice.value)).toEqual(['1', '3'])
    })

    test('Enter adds the first matching search result rather than removing an already-selected choice', async () => {
        window.__testSource = makeMultiSource(
            [
                {value: '1', label: 'Alpha'},
                {value: '2', label: 'Beta'},
            ],
            {selected: ['1']}
        )
        await mount(multiSelectHtml())

        const data = Alpine.$data(document.getElementById('root'))
        const searchInput = document.querySelector('[x-ref="searchInput"]')

        data.open()
        await settle()

        searchInput.value = 'bet'
        searchInput.dispatchEvent(new Event('input', {bubbles: true}))
        await settle()
        expect(data.activeIndex).toBe(1)

        pressKey(searchInput, 'Enter')
        await settle()
        expect(window.__testSource.selectedChoices.map(choice => choice.value)).toEqual(['1', '2'])
    })
})
