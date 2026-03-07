let loadingOverlayTimeout = null;
let loadingSpinnerTimeout = null;

const DEFAULT_LOADING_DURATION = 60000;

/**
 * Toggles paging loading state by darkening screen and displaying loading spinner
 * @param duration {number} - Maximum duration for loading overlay before being removed
 */
function toggleLoadingOverlay(duration = DEFAULT_LOADING_DURATION) {
    let body = document.body;

    if (loadingOverlayTimeout) {
        clearTimeout(loadingOverlayTimeout);
        loadingOverlayTimeout = null;
    }

    if (body.classList.contains('darken-background')) {
        body.classList.remove('darken-background');
        toggleLoadingSpinner(duration);
    } else {
        body.classList.add('darken-background');
        toggleLoadingSpinner(duration);

        loadingOverlayTimeout = setTimeout(() => {
            body.classList.remove('darken-background');
            let spinner = document.getElementById('loading-icon');
            spinner.classList.add('d-none');
            loadingOverlayTimeout = null;
        }, duration);
    }
}

/**
 * Toggles display for loading spinner
 * @param duration {number} - Maximum duration for loading overlay before being removed
 */
function toggleLoadingSpinner(duration = DEFAULT_LOADING_DURATION) {
    let spinner = document.getElementById('loading-icon');

    if (loadingSpinnerTimeout) {
        clearTimeout(loadingSpinnerTimeout);
        loadingSpinnerTimeout = null;
    }

    if (spinner.classList.contains('d-none')) {
        spinner.classList.remove('d-none');

        if (duration !== null) {
            loadingSpinnerTimeout = setTimeout(() => {
                spinner.classList.add('d-none');
                loadingSpinnerTimeout = null;
            }, duration);
        }
    } else {
        spinner.classList.add('d-none');
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
    );
}