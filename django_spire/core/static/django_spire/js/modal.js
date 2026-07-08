/**
 * Quick accessor to dispatch a modal and pass in x-data context
 * @param htmlContent {string}
 * @param eventData {Object}
 * @param dialogClasses {string}
 */
function dispatch_modal(
    htmlContent,
    {
        eventData = {},
        dialogClasses = ''
    } = {}
) {
    window.dispatchEvent(
        new CustomEvent(
            'dispatch-modal', {
                detail: {
                    'htmlContent': htmlContent,
                    'eventData': eventData,
                    'dialogClasses': dialogClasses,
                },
                bubbles: true
            }
        )
    )
}

/**
 * Quick accessor to dispatch a modal by fetching the template using Glue.view and pass in x-data context
 * @param url {string}
 * @param payload {Object}
 * @param eventData {Object}
 * @param dialogClasses {string}
 * @returns {Promise<void>}
 */
async function dispatch_modal_view(
    url,
    {
        payload = {},
        eventData = {},
        dialogClasses = ''
    } = {}
) {
    let html = await Glue.view(url).get(payload);
    dispatch_modal(html, eventData, dialogClasses);
}

