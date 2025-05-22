function dispatch_modal(html_content) {
    window.dispatchEvent(
        new CustomEvent(
            'dispatch-modal',
            { detail: {'html_content': html_content}, bubbles: true }
        )
    )
}


async function dispatch_modal_view(url, payload = {}) {
    let view = new ViewGlue(url);
    let html = await view.get(payload);
    dispatch_modal(html);
}

