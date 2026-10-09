/**
 * A button that runs one awaited call, and is off until that call settles.
 *
 *     <button x-data="asyncButton(() => component.save())" x-bind="button">Save</button>
 *
 * `isRunning` is true for the length of this button's own call.
 *
 * `busyName` names a flag in an enclosing scope. The button sets it for the
 * length of its call and is off while it is set, so buttons that name the
 * same flag take turns:
 *
 *     <div x-data="{ isSettling: false }">
 *         <button x-data="asyncButton(() => component.cancel(), 'isSettling')" x-bind="button">
 *         <button x-data="asyncButton(() => component.confirm(), 'isSettling')" x-bind="button">
 *     </div>
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('asyncButton', (call, busyName = null) => ({
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

        button: {
            ['@click']() {
                return this.run();
            },
            [':disabled']() {
                return this.isBusy;
            },
        },
    }));
});
