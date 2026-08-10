/**
 * Alpine.js directives for setting element properties (not attributes).
 * Useful for passing complex objects to Lit components.
 *
 * x-prop:name - Set a single property
 *   <task-item x-prop:item="item"></task-item>
 *
 * x-props - Set multiple properties from an object
 *   <task-item x-props="{ item: item, showActions: true }"></task-item>
 */
document.addEventListener('alpine:init', () => {
    // Single property: x-prop:name="value"
    Alpine.directive('prop', (el, { expression, modifiers }, { evaluateLater, effect }) => {
        const propName = modifiers[0] || expression.split('=')[0]?.trim();
        const evaluate = evaluateLater(expression);

        effect(() => {
            evaluate(value => {
                el[propName] = value;
            });
        });
    });

    // Multiple properties: x-props="{ prop1: value1, prop2: value2 }"
    Alpine.directive('props', (el, { expression }, { evaluateLater, effect }) => {
        const evaluate = evaluateLater(expression);

        effect(() => {
            evaluate(props => {
                if (props && typeof props === 'object') {
                    for (const [key, value] of Object.entries(props)) {
                        el[key] = value;
                    }
                }
            });
        });
    });
});
