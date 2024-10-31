function div_to_form_data(div){
    let inputs = div.querySelectorAll('input, textarea, select'); // Select all input, textarea, and select elements

    let formData = new FormData();

    inputs.forEach(input => {
        if (input.name) {
            formData.append(input.name, input.value);
        }
    });
    return formData
}


function dispatch_modal(html_content) {
    window.dispatchEvent(
        new CustomEvent(
            'dispatch-modal',
            { detail: {'html_content': html_content}, bubbles: true }
        )
    )
}


function toggle_loading_overlay() {
    let body = document.body;
    let spinner = document.getElementById('loading-icon')
    if (body.classList.contains('darken-background')) {
        body.classList.remove('darken-background');
        spinner.classList.add('d-none')
    } else {
        body.classList.add('darken-background');
        spinner.classList.remove('d-none');

    }
}


function dispatchSuccessNotification(message){
    window.dispatchEvent(new CustomEvent('notify', { detail: {'type': 'success', 'message': message}, bubbles: true }))
}


function dispatchErrorNotification(message){
    window.dispatchEvent(new CustomEvent('notify', { detail: {'type': 'error', 'message': message}, bubbles: true }))
}

