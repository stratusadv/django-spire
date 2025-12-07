class ProgressStream {
    constructor(url, config = {}) {
        this.url = url;
        this.is_running = false;
        this.poll_interval = null;

        this.config = {
            on_update: config.on_update || (() => {}),
            on_complete: config.on_complete || (() => {}),
            on_error: config.on_error || (() => {}),
            redirect_on_complete: config.redirect_on_complete || null,
            redirect_delay: config.redirect_delay || 1000,
            poll_interval: config.poll_interval || 1000
        };
    }

    async start() {
        if (this.is_running) return;

        this.is_running = true;
        this._start_polling();
    }

    stop() {
        if (!this.is_running) return;

        this.is_running = false;

        if (this.poll_interval) {
            clearInterval(this.poll_interval);
            this.poll_interval = null;
        }
    }

    _start_polling() {
        this._poll();

        this.poll_interval = setInterval(() => {
            if (this.is_running) {
                this._poll();
            }
        }, this.config.poll_interval);
    }

    async _poll() {
        try {
            let response = await fetch(this.url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': get_cookie('csrftoken'),
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            let data = await response.json();

            this.config.on_update(data);

            if (data.step === 'error') {
                this.config.on_error(data);
                this.stop();
                return;
            }

            if (data.progress >= 100) {
                this.config.on_complete(data);
                this.stop();
                this._redirect();
            }
        } catch (error) {
            console.warn('Poll error:', error.message);
        }
    }

    _redirect() {
        if (!this.config.redirect_on_complete) return;

        setTimeout(() => {
            window.location.href = this.config.redirect_on_complete;
        }, this.config.redirect_delay);
    }
}

window.ProgressStream = ProgressStream;
