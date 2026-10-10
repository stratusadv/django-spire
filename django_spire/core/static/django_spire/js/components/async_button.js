/**
 * A button that runs one awaited call, and is off until that call settles.
 *
 *     <button x-bind="asyncButton(() => component.save())">Save</button>
 *
 * `isRunning` is true for the length of this button's own call.
 *
 * `busyName` names a flag in an enclosing scope. The button sets it for the
 * length of its call and is off while it is set, so buttons that name the
 * same flag take turns:
 *
 *     <div x-data="{ isSettling: false }">
 *         <button x-bind="asyncButton(() => component.cancel(), 'isSettling')">
 *         <button x-bind="asyncButton(() => component.confirm(), 'isSettling')">
 *     </div>
 *
 * The binding gives the element its own x-data. An element that needs to set
 * x-data itself uses the data component and binds its `button`:
 *
 *     <button x-data="asyncButton(() => component.save())" x-bind="button">
 */
document.addEventListener('alpine:init', () => {
    const button = {
        ['@click']() {
            return this.run();
        },
        [':disabled']() {
            return this.isBusy;
        },
    };

    const asyncButton = (call, busyName = null) => ({
        button,
        isRunning: false,

        get isBusy() {
            return this.isRunning || Boolean(busyName && this[busyName]);
        },

        async run() {
            if (this.isBusy) {
                return;
            }

            this.isRunning = true;

            if (busyName) {
                this[busyName] = true;
            }

            try {
                await call();
            } finally {
                this.isRunning = false;

                if (busyName) {
                    this[busyName] = false;
                }
            }
        },
    });

    Alpine.data('asyncButton', asyncButton);

    Alpine.bind('asyncButton', (call, busyName = null) => ({
        ['x-data']() {
            return asyncButton(call, busyName);
        },
        ...button,
    }));
});
