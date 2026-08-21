Spire.ajax = {
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
                'X-CSRFToken': Spire.cookie.get('csrftoken'),
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

        if (response.ok) {
            const text = await response.text();
            result.data = text ? JSON.parse(text) : null;
        }

        if (!response.ok) {
            throw result;
        }

        return result;
    }
};
