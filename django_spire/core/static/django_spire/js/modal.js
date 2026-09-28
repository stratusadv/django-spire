Spire.modal = {
    _pendingClose: null,
    _result: undefined,

    /**
     * Close the dispatch modal, optionally reporting an outcome to whoever
     * opened it. dispatchGlueComponent()'s and dispatchGlueHtml()'s promises
     * resolve with `result`; a modal dismissed any other way (Cancel, the X,
     * Escape, the backdrop) resolves undefined, so "completed" and "dismissed"
     * stay distinguishable.
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
     * Show a Glue component in the dispatch modal.
     * The content arrives with its own proxies already registered, so it takes
     * no scopeData. The component is rendered here and disposed on close.
     *
     * Resolves when the modal CLOSES, with whatever the content passed to
     * Spire.modal.close(). Subscribe to an owned child's events before
     * dispatching; the returned component already carries its children:
     *
     *     @click="
     *         const modal = await component.edit_entry_modal({ entry_id: 12 })
     *         modal.time_entry.form.$on('saved', () => component.$refresh())
     *         await Spire.modal.dispatchGlueComponent(modal, { dialogClasses: 'modal-lg' })
     *     "
     *
     * For the result of a Glue attribute declared with @Glue.html_attr, use
     * dispatchGlueHtml() instead.
     *
     * @param {Promise<*>|*} glueComponent
     * @param {object} [options={}]
     * @param {object} [options.eventData={}]
     * @param {string} [options.dialogClasses='']
     * @param {boolean} [options.renderToBody=true]
     * @returns {Promise<*>} the outcome, or undefined if dismissed
     */
    async dispatchGlueComponent(
        glueComponent,
        {eventData = {}, dialogClasses = '', renderToBody = true} = {},
    ) {
        const component = await glueComponent;
        if (!component || typeof component !== 'object' || !('$el' in component)
            || typeof component.render !== 'function' || typeof component.$dispose !== 'function') {
            throw new Error(
                `Spire.modal.dispatchGlueComponent() expects a Glue component object. ` +
                `Received ${component?.constructor?.name ?? String(component)}. ` +
                `For the result of a Glue attribute declared with @Glue.html_attr, ` +
                `use Spire.modal.dispatchGlueHtml() instead.`
            );
        }

        try {
            const rendered = await component.render();
            if (typeof rendered?.html !== 'string') {
                throw new Error(
                    `Spire.modal.dispatchGlueComponent(): the component did not render ` +
                    `to { html }. Received ${rendered?.constructor?.name ?? String(rendered)}.`
                );
            }

            const closed = new Promise(resolve => Spire.modal._settleOnClose(resolve));
            Spire.modal.dispatch(rendered.html, {eventData, dialogClasses, renderToBody});

            return await closed;
        } finally {
            const root = component.$el;
            component.$dispose();
            root?.remove();
        }
    },

    /**
     * Show the HTML returned by a Glue attribute declared with @Glue.html_attr.
     * The result resolves to `{ html: string }` and is dispatched as-is.
     *
     * Resolves when the modal CLOSES, with whatever the content passed to
     * Spire.modal.close(), or undefined if dismissed.
     *
     * For a Glue component object, use dispatchGlueComponent() instead.
     *
     * @param {Promise<*>|*} glueHtmlResult
     * @param {object} [options={}]
     * @param {object} [options.eventData={}]
     * @param {string} [options.dialogClasses='']
     * @param {boolean} [options.renderToBody=true]
     * @returns {Promise<*>} the outcome, or undefined if dismissed
     */
    async dispatchGlueHtml(
        glueHtmlResult,
        {eventData = {}, dialogClasses = '', renderToBody = true} = {},
    ) {
        const result = await glueHtmlResult;
        if (typeof result?.html !== 'string') {
            const hint = typeof result === 'string'
                ? `Received the rendered text, which is what a plain @Glue.attr ` +
                  `returning a TemplateResponse resolves to: its markup would show, ` +
                  `but the proxies it binds to would never be registered.`
                : `Received ${result?.constructor?.name ?? String(result)}.`;

            throw new Error(
                `Spire.modal.dispatchGlueHtml() expects the result of a Glue attribute ` +
                `declared with @Glue.html_attr. ${hint}`
            );
        }

        const closed = new Promise(resolve => Spire.modal._settleOnClose(resolve));
        Spire.modal.dispatch(result.html, {eventData, dialogClasses, renderToBody});

        return closed;
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
     *     undefined if dismissed -- the same contract as dispatchGlueComponent()
     *     and dispatchGlueHtml()
     */
    async dispatchView(url, {payload = {}, eventData = {}, dialogClasses = 'modal-dialog-centered', renderToBody = true} = {}) {
        let htmlContent = await Glue.view(url).get(payload);
        const closed = new Promise(resolve => Spire.modal._settleOnClose(resolve));
        Spire.modal.dispatch(htmlContent, {eventData, dialogClasses, renderToBody});

        return closed;
    }
};
