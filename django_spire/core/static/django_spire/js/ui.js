let loadingOverlayTimeout = null;
let loadingSpinnerTimeout = null;
const DEFAULT_LOADING_DURATION = 60000;

window.addEventListener('popstate', () => {
    let spinner = document.getElementById('loading-icon');
    spinner.classList.add('d-none');
    if (loadingSpinnerTimeout) {
        clearTimeout(loadingSpinnerTimeout);
        loadingSpinnerTimeout = null;
    }
});

window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
        let spinner = document.getElementById('loading-icon');
        spinner.classList.add('d-none');
        if (loadingSpinnerTimeout) {
            clearTimeout(loadingSpinnerTimeout);
            loadingSpinnerTimeout = null;
        }
    }
});

Spire.ui = {
    /**
     * @param {number} [duration=60000] - Maximum duration for loading overlay before being removed
     */
    toggleLoadingOverlay(duration = DEFAULT_LOADING_DURATION) {
        let body = document.body;

        if (loadingOverlayTimeout) {
            clearTimeout(loadingOverlayTimeout);
            loadingOverlayTimeout = null;
        }

        if (body.classList.contains('darken-background')) {
            body.classList.remove('darken-background');
            Spire.ui.toggleLoadingSpinner(duration);
        } else {
            body.classList.add('darken-background');
            Spire.ui.toggleLoadingSpinner(duration);

            loadingOverlayTimeout = setTimeout(() => {
                body.classList.remove('darken-background');
                let spinner = document.getElementById('loading-icon');
                spinner.classList.add('d-none');
                loadingOverlayTimeout = null;
            }, duration);
        }
    },

    /**
     * @param {number} [duration=60000] - Maximum duration for loading overlay before being removed
     */
    toggleLoadingSpinner(duration = DEFAULT_LOADING_DURATION) {
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
    },

    /**
     * @param {Element} el
     * @returns {boolean}
     */
    hasContent(el) {
        return Array.from(el.childNodes).some(
            node => {
                if (node.nodeType === Node.TEXT_NODE) {
                    return node.textContent.trim() !== '';
                }
                return node.nodeType === Node.ELEMENT_NODE;
            }
        );
    }
};