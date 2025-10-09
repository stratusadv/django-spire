class ProgressStream {
    constructor(url, config = {}) {
        this.url = url;
        this.event_source = null;
        this.config = {
            on_update: config.on_update || (() => {}),
            on_complete: config.on_complete || (() => {}),
            on_error: config.on_error || (() => {}),
            redirect_on_complete: config.redirect_on_complete || null,
            redirect_delay: config.redirect_delay || 1000
        };
    }

    start() {
        this.event_source = new EventSource(this.url);

        this.event_source.onmessage = (event) => {
            const data = JSON.parse(event.data);

            this.config.on_update(data);

            if (data.step === 'error') {
                this.config.on_error(data);
                this.stop();

                return;
            }

            if (data.progress >= 100) {
                this.config.on_complete(data);
                this.stop();

                if (this.config.redirect_on_complete) {
                    setTimeout(() => {
                        window.location.href = this.config.redirect_on_complete;
                    }, this.config.redirect_delay);
                }
            }
        };

        this.event_source.onerror = (error) => {
            console.error('ProgressStream error:', error);

            this.config.on_error({
                step: 'error',
                message: 'Connection error',
                progress: 0
            });

            this.stop();
        };
    }

    stop() {
        if (this.event_source) {
            this.event_source.close();
            this.event_source = null;
        }
    }
}

window.ProgressStream = ProgressStream;
