async function dispatch_modal_view(url, payload = {}) {
    let view = new GlueView(url);
    let html = await view.get(payload);
    dispatch_modal(html);
}
