function dispatchModal(
    htmlContent,
    {
        eventData = {},
        dialogClasses = '',
        renderToBody = true,
    } = {}
) {
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
    )
}

async function dispatchElementByIdToModal(
    elementId,
    {
        eventData = {},
        dialogClasses = '',
        renderToBody = true,
    } = {}
) {
    let htmlContent = document.getElementById(elementId).innerHTML
    dispatchModal(htmlContent, {eventData, dialogClasses, renderToBody})
}

async function dispatchViewToModal(
    url,
    {
        payload = {},
        eventData = {},
        dialogClasses = '',
        renderToBody = true,
    } = {}
) {
    let htmlContent = await Glue.view(url).get(payload)
    console.log(htmlContent)
    dispatchModal(htmlContent, {eventData, dialogClasses, renderToBody})
}

