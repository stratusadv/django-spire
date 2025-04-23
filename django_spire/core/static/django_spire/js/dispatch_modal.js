async function dispatch_modal_view(url, payload = {}) {
    let view = new ViewGlue(url);
    let html = await view.get(payload);
    dispatch_modal(html);
}
