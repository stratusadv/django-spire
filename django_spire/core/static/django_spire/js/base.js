function div_to_form_data(div) {
    let inputs = div.querySelectorAll('input, textarea, select');

    let formData = new FormData();

    inputs.forEach(input => {
        if (input.name) {
            formData.append(input.name, input.value);
        }
    });

    return formData
}


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


function dispatch_success_notification(message){
    window.dispatchEvent(
        new CustomEvent(
            'notify',
            { detail: {'type': 'success', 'message': message}, bubbles: true }
        )
    )
}


function dispatch_error_notification(message){
    window.dispatchEvent(
        new CustomEvent(
            'notify',
            { detail: {'type': 'error', 'message': message}, bubbles: true }
        )
    )
}

