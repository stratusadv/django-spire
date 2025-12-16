class ProgressStream {
    constructor(url, config = {}) {
        this.url = url;

        this.config = {
            on_complete: config.on_complete || (() => {}),
            on_error: config.on_error || (() => {}),
            on_update: config.on_update || (() => {}),
            redirect_delay: config.redirect_delay || 1000,
            redirect_url: config.redirect_url || null,
        };
    }

    _redirect() {
        if (!this.config.redirect_url) {
            return;
        }

        setTimeout(() => {
            window.location.href = this.config.redirect_url;
        }, this.config.redirect_delay);
    }

    async start() {
        let response = await fetch(this.url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': get_cookie('csrftoken'),
            },
        });

        if (!response.ok) {
            this.config.on_error({ message: `HTTP ${response.status}` });
            return;
        }

        let reader = response.body.getReader();
        let decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            let { done, value } = await reader.read();

            if (done) {
                break;
            }

            buffer += decoder.decode(value, { stream: true });
            let lines = buffer.split('\n');

            buffer = lines.pop();

            for (let line of lines) {
                if (!line.trim()) {
                    continue;
                }

                let data = JSON.parse(line);

                this.config.on_update(data);

                if (data.status === 'error') {
                    this.config.on_error(data);
                    return;
                }

                if (data.status === 'complete') {
                    this.config.on_complete(data);
                    this._redirect();
                    return;
                }
            }
        }
    }
}

window.ProgressStream = ProgressStream;
