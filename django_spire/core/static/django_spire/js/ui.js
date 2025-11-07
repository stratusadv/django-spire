function toggle_loading_overlay() {
    let body = document.body;
    let spinner = document.getElementById('loading-icon');

    if (body.classList.contains('darken-background')) {
        body.classList.remove('darken-background');
        spinner.classList.add('d-none');
    } else {
        body.classList.add('darken-background');
        spinner.classList.remove('d-none');
    }
}

function has_content(el) {
    return Array.from(el.childNodes).some(
        node => {
            if (node.nodeType === Node.TEXT_NODE) {
                return node.textContent.trim() !== '';
            }
            return node.nodeType === Node.ELEMENT_NODE;

        }
    )
}