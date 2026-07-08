function dispatchModal(
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

async function dispatchElementToModal(
    elementId,
    {
        eventData = {},
        dialogClasses = ''
    } = {}
) {
    let htmlContent = document.getElementById(elementId).innerHTML
    dispatchModal(htmlContent, {eventData, dialogClasses})
}

async function dispatchViewToModal(
    url,
    {
        payload = {},
        eventData = {},
        dialogClasses = ''
    } = {}
) {
    let htmlContent = await Glue.view(url).get(payload)
    dispatchModal(htmlContent, {eventData, dialogClasses})
}

