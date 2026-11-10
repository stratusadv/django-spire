Spire.widget = Spire.widget || {};

/**
 * A choice source for multiSearchAndSelect over any list of chosen values,
 * such as a Glue component's editable attribute:
 *
 *     Spire.widget.choiceSource({
 *         choices: [{value: 'ast', label: 'Asset'}, {value: 'exp', label: 'Expense'}],
 *         getSelected: () => component.account_types,
 *         setSelected: (values) => component.account_types = values,
 *     })
 *
 * `getSelected` reads the chosen values and `setSelected` replaces them.
 * Chosen choices are listed in the order of `choices`.
 *
 * @param {object} options
 * @param {{value: *, label: string}[]} options.choices
 * @param {function(): *[]} options.getSelected
 * @param {function(*[]): void} options.setSelected
 */
Spire.widget.choiceSource = ({choices, getSelected, setSelected}) => ({
    choices,

    get selectedChoices() {
        const selected = new Set((getSelected() || []).map(String));
        return choices.filter(choice => selected.has(String(choice.value)));
    },

    addChoice(value) {
        setSelected([...(getSelected() || []), value]);
    },

    removeChoice(value) {
        setSelected((getSelected() || []).filter(existing => String(existing) !== String(value)));
    },
});
