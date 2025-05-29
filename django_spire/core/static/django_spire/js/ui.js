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
