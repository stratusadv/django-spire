class ProgressStream {
    constructor(url, config = {}) {
        this.url = url;
        this.controller = null;
        this.is_running = false;

        this.config = {
            on_update: config.on_update || (() => {}),
            on_complete: config.on_complete || (() => {}),
            on_error: config.on_error || (() => {}),
            redirect_on_complete: config.redirect_on_complete || null,
            redirect_delay: config.redirect_delay || 1000
        };
    }

    async start() {
        if (this.is_running) return;

        this.is_running = true;
        this.controller = new AbortController();

        try {
            let response = await this._fetch();

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            await this._read_stream(response);
        } catch (error) {
            this._handle_error(error);
        }
    }

    stop() {
        if (!this.is_running) return;

        this.is_running = false;

        if (this.controller) {
            this.controller.abort();
            this.controller = null;
        }
    }

    async _fetch() {
        return fetch(this.url, {
            method: 'POST',
            signal: this.controller.signal,
            headers: {
                'X-CSRFToken': get_cookie('csrftoken'),
            }
        });
    }

    async _read_stream(response) {
        let reader = response.body.getReader();
        let decoder = new TextDecoder();
        let buffer = '';

        while (this.is_running) {
            let { done, value } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            buffer = this._process_buffer(buffer);
        }
    }

    _process_buffer(buffer) {
        let lines = buffer.split('\n');
        let remainder = lines.pop();

        for (let line of lines) {
            if (line.startsWith('data: ')) {
                this._handle_message(line.slice(6));
            }
        }

        return remainder;
    }

    _handle_message(json_string) {
        let data;

        try {
            data = JSON.parse(json_string);
        } catch {
            return;
        }

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
    }

    _handle_error(error) {
        if (error.name === 'AbortError') return;

        console.error('ProgressStream error:', error);

        this.config.on_error({
            step: 'error',
            message: 'Connection error',
            progress: 0
        });

        this.stop();
    }

    _redirect() {
        if (!this.config.redirect_on_complete) return;

        setTimeout(() => {
            window.location.href = this.config.redirect_on_complete;
        }, this.config.redirect_delay);
    }
}

window.ProgressStream = ProgressStream;
