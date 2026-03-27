/**
 * Quick accessor to dispatch a modal and pass in x-data conext
 * @param html_content {HTML}
 * @param eventData {Object}
 */
function dispatch_modal(html_content, eventData = {}) {
    window.dispatchEvent(
        new CustomEvent(
            'dispatch-modal', {
                detail: {
                    'html_content': html_content,
                    'eventData': eventData
                },
                bubbles: true
            }
        )
    )
}

/**
 * Quick accessor to dispatch a modal by fetching the template using ViewGlue and pass in x-data context
 * @param url {string}
 * @param payload {Object}
 * @param eventData {Object}
 * @returns {Promise<void>}
 */
async function dispatch_modal_view(url, payload = {}, eventData = {}) {
    let view = new ViewGlue(url);
    let html = await view.get(payload);
    dispatch_modal(html, eventData);
}

