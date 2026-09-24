Spire.modal = {
    _pendingClose: null,
    _result: undefined,

    /**
     * Close the dispatch modal, optionally reporting an outcome to whoever
     * opened it. dispatchGlue()'s promise resolves with `result`; a modal
     * dismissed any other way (Cancel, the X, Escape, the backdrop) resolves
     * undefined, so "completed" and "dismissed" stay distinguishable.
     *
     * @param {*} [result]
     */
    close(result) {
        Spire.modal._result = result;
        bootstrap.Modal
            .getOrCreateInstance(document.getElementById('baseDispatchModal'))
            .hide();
    },

    _settleOnClose(resolve) {
        const element = document.getElementById('baseDispatchModal');

        Spire.modal._pendingClose?.(undefined);
        Spire.modal._pendingClose = resolve;

        if (element.dataset.spireCloseWatched) {
            return;
        }

        element.dataset.spireCloseWatched = 'true';
        element.addEventListener('hidden.bs.modal', () => {
            const pending = Spire.modal._pendingClose;
            const result = Spire.modal._result;
            Spire.modal._pendingClose = null;
            Spire.modal._result = undefined;
            pending?.(result);
        });
    },

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
     * Show a Glue component or the HTML returned by @Glue.html_attr.
     * The content arrives with its own proxies already registered, so it takes
     * no scopeData. A component is rendered here and disposed on close.
     *
     * Resolves when the modal CLOSES, with whatever the content passed to
     * Spire.modal.close(). A component can expose an event from an owned form:
     *
     *     @click="
     *         const modal = await component.edit_entry_modal({ entry_id: 12 })
     *         modal.$on('saved', () => component.$refresh())
     *         await Spire.modal.dispatchGlue(modal, { dialogClasses: 'modal-lg' })
     *     "
     *
     * @param {Promise<*>|*} glueHtmlResult
     * @param {object} [options={}]
     * @param {object} [options.eventData={}]
     * @param {string} [options.dialogClasses='']
     * @param {boolean} [options.renderToBody=true]
     * @returns {Promise<*>} the outcome, or undefined if dismissed
     */
    async dispatchGlue(glueHtmlResult, {eventData = {}, dialogClasses = '', renderToBody = true} = {}) {
        const result = await glueHtmlResult;
        const component = result && typeof result === 'object' && '$el' in result
            && typeof result.render === 'function' && typeof result.$dispose === 'function'
            ? result : null;

        try {
            const rendered = component ? await component.render() : result;
            if (typeof rendered?.html !== 'string') {
                const hint = typeof rendered === 'string'
                    ? `Received the rendered text, which is what a plain @Glue.attr ` +
                      `returning a TemplateResponse resolves to: its markup would show, ` +
                      `but the proxies it binds to would never be registered.`
                    : `Received ${rendered?.constructor?.name ?? String(rendered)}.`;

                throw new Error(
                    `Spire.modal.dispatchGlue() expects a Glue component or the result ` +
                    `of a Glue attribute declared with @Glue.html_attr. ${hint}`
                );
            }

            const closed = new Promise(resolve => Spire.modal._settleOnClose(resolve));
            Spire.modal.dispatch(rendered.html, {eventData, dialogClasses, renderToBody});

            return await closed;
        } finally {
            if (component) {
                const root = component.$el;
                component.$dispose();
                root?.remove();
            }
        }
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
     * @returns {Promise<*>} the outcome passed to Spire.modal.close(), or
     *     undefined if dismissed -- the same contract as dispatchGlue()
     */
    async dispatchView(url, {payload = {}, eventData = {}, dialogClasses = 'modal-dialog-centered', renderToBody = true} = {}) {
        let htmlContent = await Glue.view(url).get(payload);
        const closed = new Promise(resolve => Spire.modal._settleOnClose(resolve));
        Spire.modal.dispatch(htmlContent, {eventData, dialogClasses, renderToBody});

        return closed;
    }
};
