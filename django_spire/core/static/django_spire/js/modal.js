Spire.modal = {
    open(elementId, data = {}, options = {}) {
        const element = document.getElementById(elementId);

        if (!element?.hasAttribute('data-spire-modal')) {
            throw new Error(
                `Spire modal "${elementId}" is not defined. ` +
                `Register it with the Django template tag ` +
                `{% define_modal id='${elementId}' template='path/to/modal.html' %}.`
            );
        }

        return Spire.modal.dispatchElementById(elementId, {
            dialogClasses: options.dialogClasses || '',
            renderToBody: options.renderToBody ?? true,
            scopeData: data,
        });
    },

    /**
     * @param {string} htmlContent
     * @param {object} [options={}]
     * @param {object} [options.eventData={}]
     * @param {string} [options.dialogClasses='']
     * @param {boolean} [options.renderToBody=true]
     */
    dispatch(htmlContent, {eventData = {}, dialogClasses = '', renderToBody = true, scopeData = null} = {}) {
        window.dispatchEvent(
            new CustomEvent(
                'dispatch-modal', {
                    detail: {
                        'htmlContent': htmlContent,
                        'eventData': eventData,
                        'dialogClasses': dialogClasses,
                        'renderToBody': renderToBody,
                        'scopeData': scopeData,
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
    async dispatchElementById(elementId, {eventData = {}, dialogClasses = '', renderToBody = true, scopeData = null} = {}) {
        let htmlContent = document.getElementById(elementId).innerHTML;
        Spire.modal.dispatch(htmlContent, {eventData, dialogClasses, renderToBody, scopeData});
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
        Spire.modal.dispatch(htmlContent, {eventData, dialogClasses, renderToBody});
    }
};
