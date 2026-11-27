import {afterEach, describe, expect, test} from 'bun:test'

import {mount, settle} from './utils.js'

afterEach(() => {
    document.body.innerHTML = ''
    delete window.__testSource
    delete window.__testActionChoices
    delete window.__testComboboxOptions
    delete window.__testComboboxSelect
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

function singleSelectHtml({includeEmpty = false, withActionChoices = false} = {}) {
    return `
        <div
            id="root"
            ${includeEmpty ? 'data-include-empty="true"' : ''}
            x-data="searchAndSelect(window.__testSource${withActionChoices ? ', () => (window.__testActionChoices || [])' : ''})"
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
                ${withActionChoices ? `
                    <template x-for="(actionChoice, actionIndex) in actionChoices" :key="actionChoice.label">
                        <button
                            type="button"
                            x-bind="dropdownOption(() => choiceCount + actionIndex)"
                            @click="runActionChoice(actionChoice)"
                            x-text="actionChoice.label"
                        ></button>
                    </template>
                ` : ''}
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

    test('highlights the initial or selected choice when choices load asynchronously after open', async () => {
        window.__testSource = Alpine.reactive(makeSingleSource([], {value: 'b', searchable: true}))
        await mount(singleSelectHtml())

        const data = Alpine.$data(document.getElementById('root'))

        data.openDropdown()
        await settle()
        expect(data.activeIndex).toBe(-1)

        window.__testSource.choices = [
            {value: 'a', label: 'Alpha'},
            {value: 'b', label: 'Beta'},
        ]
        await settle()
        expect(data.activeIndex).toBe(1)
    })

    test('arrows reach action choices and Enter invokes onClick with the search query without changing value', async () => {
        const invoked = []
        window.__testSource = makeSingleSource([
            {value: 'a', label: 'Alpha'},
            {value: 'b', label: 'Beta'},
        ])
        window.__testActionChoices = [
            {label: 'Add a new customer', onClick: query => invoked.push(query)},
        ]
        await mount(singleSelectHtml({withActionChoices: true}))

        const data = Alpine.$data(document.getElementById('root'))
        const searchInput = document.querySelector('[x-ref="searchInput"]')

        data.openDropdown()
        await settle()
        expect(data.activeIndex).toBe(0)

        pressKey(searchInput, 'ArrowDown')
        pressKey(searchInput, 'ArrowDown')
        expect(data.activeIndex).toBe(2)

        pressKey(searchInput, 'Enter')
        await settle()
        expect(invoked).toEqual([''])
        expect(window.__testSource.value).toBeNull()
        expect(data.showDropdown).toBe(false)

        // When no choice matches the search query, the action choice is highlighted and gets the query.
        data.openDropdown()
        await settle()
        searchInput.value = 'New Co'
        searchInput.dispatchEvent(new Event('input', {bubbles: true}))
        await settle()
        expect(data.activeIndex).toBe(0)

        pressKey(searchInput, 'Enter')
        await settle()
        expect(invoked).toEqual(['', 'New Co'])
        expect(window.__testSource.value).toBeNull()
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

    test('highlights the first enabled choice when choices load asynchronously after open', async () => {
        window.__testSource = Alpine.reactive(makeMultiSource([], {disabled: ['1'], searchable: true}))
        await mount(multiSelectHtml())

        const data = Alpine.$data(document.getElementById('root'))

        data.open()
        await settle()
        expect(data.activeIndex).toBe(-1)

        window.__testSource.choices = [
            {value: '1', label: 'Blocked'},
            {value: '2', label: 'Beta'},
        ]
        await settle()
        expect(data.activeIndex).toBe(1)
    })
})

function comboboxHtml() {
    return `
        <div
            id="root"
            x-data="combobox(window.__testSource, () => (window.__testComboboxOptions || []), option => window.__testComboboxSelect?.(option))"
        >
            <input
                x-ref="input"
                type="text"
                role="combobox"
                :value="inputValue"
                @focus="openDropdown()"
                @click="openDropdown()"
                @input="onInput($event.target.value)"
                @keydown.arrow-down.prevent="moveActive(1)"
                @keydown.arrow-up.prevent="moveActive(-1)"
                @keydown.enter="if (showDropdown && activeIndex >= 0) { $event.preventDefault(); activateActive() }"
                @keydown.escape.stop="closeDropdown()"
            >
            <div x-ref="dropdown" role="listbox" x-show="showDropdown && filteredOptions.length > 0">
                <template x-for="(option, index) in filteredOptions" :key="option.value + '-' + index">
                    <div
                        x-bind="dropdownOption(() => index)"
                        @click="selectOption(option)"
                        x-text="option.label"
                    ></div>
                </template>
            </div>
        </div>
    `
}

describe('combobox keyboard navigation and freeform entry', () => {
    test('opens on click, filters as typed, preserves freeform text, and selects on ArrowDown + Enter', async () => {
        const selected = []
        window.__testSource = {value: ''}
        window.__testComboboxOptions = [
            {value: 'Brand strategy', label: 'Brand strategy', unit_price: '750.00'},
            {value: 'Lawn mowing', label: 'Lawn mowing', unit_price: '45.00'},
        ]
        window.__testComboboxSelect = option => selected.push(option)
        await mount(comboboxHtml())

        const data = Alpine.$data(document.getElementById('root'))
        const input = document.querySelector('[x-ref="input"]')

        data.openDropdown()
        await settle()
        expect(data.showDropdown).toBe(true)
        expect(data.activeIndex).toBe(-1)
        expect(data.filteredOptions).toHaveLength(2)

        // Pressing Enter without arrowing does not hijack freeform input.
        input.value = 'Custom work'
        input.dispatchEvent(new Event('input', {bubbles: true}))
        await settle()
        expect(window.__testSource.value).toBe('Custom work')
        expect(data.showDropdown).toBe(false)
        const freeformEnter = pressKey(input, 'Enter')
        expect(freeformEnter.defaultPrevented).toBe(false)
        expect(selected).toEqual([])

        // Typing a matching prefix filters suggestions; ArrowDown + Enter picks it and fires onSelect.
        input.value = 'lawn'
        input.dispatchEvent(new Event('input', {bubbles: true}))
        await settle()
        expect(data.showDropdown).toBe(true)
        expect(data.filteredOptions.map(o => o.label)).toEqual(['Lawn mowing'])

        pressKey(input, 'ArrowDown')
        expect(data.activeIndex).toBe(0)

        const pickEnter = pressKey(input, 'Enter')
        await settle()
        expect(pickEnter.defaultPrevented).toBe(true)
        expect(window.__testSource.value).toBe('Lawn mowing')
        expect(data.showDropdown).toBe(false)
        expect(selected).toHaveLength(1)
        expect(selected[0].unit_price).toBe('45.00')
    })
})
