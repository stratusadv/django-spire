Spire.ajax = {
    /**
     * @param {string} method
     * @param {string} url
     * @param {object} data
     * @returns {Promise}
     */
    async request(method, url, data) {
        return axios({
            method: method,
            url: url,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Spire.cookie.get('csrftoken'),
            },
            data: data
        });
    }
};