Spire.modal = {
    /**
     * @param {string} htmlContent
     * @param {object} [options={}]
     * @param {object} [options.eventData={}]
     * @param {string} [options.dialogClasses='']
     * @param {boolean} [options.renderToBody=true]
     */
    dispatch(htmlContent, {eventData = {}, dialogClasses = '', renderToBody = true} = {}) {
        window.dispatchEvent(
            new CustomEvent(
                'dispatch-modal', {
                    detail: {
                        'htmlContent': htmlContent,
                        'eventData': eventData,
                        'dialogClasses': dialogClasses,
                        'renderToBody': renderToBody,
                    },
                    bubbles: true
                }
            )
        );
    },

    /**
     * @param {string} elementId
     * @param {object} [options={}]
     * @param {object} [options.eventData={}]
     * @param {string} [options.dialogClasses='']
     * @param {boolean} [options.renderToBody=true]
     */
    async dispatchElementById(elementId, {eventData = {}, dialogClasses = '', renderToBody = true} = {}) {
        let htmlContent = document.getElementById(elementId).innerHTML;
        Spire.modal.dispatch(htmlContent, {eventData, dialogClasses, renderToBody});
    },

    /**
     * @param {string} url
     * @param {object} [options={}]
     * @param {object} [options.payload={}]
     * @param {object} [options.eventData={}]
     * @param {string} [options.dialogClasses='']
     * @param {boolean} [options.renderToBody=true]
     */
    async dispatchView(url, {payload = {}, eventData = {}, dialogClasses = '', renderToBody = true} = {}) {
        let htmlContent = await Glue.view(url).get(payload);
        console.log(htmlContent);
        Spire.modal.dispatch(htmlContent, {eventData, dialogClasses, renderToBody});
    }
};