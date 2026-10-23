document.addEventListener('alpine:init', () => {
    Alpine.data('signageKiosk', (count, delay) => ({
        index: 0,
        count: count,
        delay: delay,
        rotation: null,

        init() {
            if (this.count > 1) {
                this.rotation = setInterval(() => {
                    this.next_slide();
                }, this.delay);
            }
            document.addEventListener('keydown', (event) => {
                if (event.key === 'ArrowLeft') {
                    this.previous_slide();
                    this.reset_timer();
                }
                if (event.key === 'ArrowRight') {
                    this.next_slide();
                    this.reset_timer();
                }
            });
        },

        reset_timer() {
            clearInterval(this.rotation);
            if (this.count > 1) {
                this.rotation = setInterval(() => {
                    this.next_slide();
                }, this.delay);
            }
        },

        next_slide() {
            this.index = (this.index + 1) % this.count;
        },

        previous_slide() {
            this.index = (this.index - 1);
            if (this.index < 0) {
                this.index = this.count - 1;
            }
        }
    }));
});
