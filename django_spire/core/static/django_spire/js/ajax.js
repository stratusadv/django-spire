Spire.ajax = {
    /**
     * @returns {string|null}
     */
    getCsrfToken() {
        const meta = document.querySelector('meta[name="spire-csrf-cookie-name"]');
        const cookieName = meta ? meta.content : 'csrftoken';
        return Spire.cookie.get(cookieName);
    },

    /**
     * @param {string} method
     * @param {string} url
     * @param {object} data
     * @returns {Promise}
     */
    async request(method, url, data) {
        const request_method = method.toUpperCase();
        const init = {
            method: request_method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Spire.ajax.getCsrfToken(),
            },
        };

        if (data !== undefined && request_method !== 'GET') {
            init.body = JSON.stringify(data);
        }

        const response = await fetch(url, init);
        const result = {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries()),
        };

        const text = await response.text();
        if (text) {
            try {
                result.data = JSON.parse(text);
            } catch (error) {
                result.data = null;
            }
        }

        if (!response.ok) {
            throw result;
        }

        return result;
    }
};
