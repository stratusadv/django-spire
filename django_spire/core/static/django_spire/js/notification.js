const DISPATCH_NOTIFY_TYPES = {
    error: 'error',
    warning: 'warning',
    info: 'info',
    success: 'success',
};

const NOTIFY_EVENT = 'notify';

const VALID_NOTIFY_TYPES = Object.values(DISPATCH_NOTIFY_TYPES);

/**
 * Convenience method to dispatch a notify event
 * @param {string} type - 'error', 'warning', 'info', 'success'
 * @param {string} message - notification message
 */
function dispatch({type, message}) {
    if (!VALID_NOTIFY_TYPES.includes(type)) {
        throw new Error('Dispatch message type invalid: ' + type);
    }

    window.dispatchEvent(
        new CustomEvent(NOTIFY_EVENT, {
            detail: {
                type: type,
                message: message,
            },
        }),
    );
}

/**
 * Convenience method to dispatch an error message
 * @param {string} message - notification message
 */
function dispatchError(message) {
    dispatch({type: DISPATCH_NOTIFY_TYPES.error, message: message});
}

/**
 * Convenience method to dispatch an info message
 * @param {string} message - notification message
 */
function dispatchInfo(message) {
    dispatch({type: DISPATCH_NOTIFY_TYPES.info, message: message});
}

/**
 * Convenience method to dispatch a success message
 * @param {string} message - notification message
 */
function dispatchSuccess(message) {
    dispatch({type: DISPATCH_NOTIFY_TYPES.success, message: message});
}

/**
 * Convenience method to dispatch a warning message
 * @param {string} message - notification message
 */
function dispatchWarning(message) {
    dispatch({type: DISPATCH_NOTIFY_TYPES.warning, message: message});
}

/**
 * Convenience method to dispatch a null or errored response
 * @param {Object} response - http response object (preferred use-case for django_spire json_response method)
 * @param {string} defaultMessage - default error message if one is not supplied in the response
 */
function tryDispatchResponseError(response, defaultMessage) {
    let message = response == null ? defaultMessage : response.message;
    let type = response == null ? DISPATCH_NOTIFY_TYPES.error : response.type;

    if (response == null || type === DISPATCH_NOTIFY_TYPES.error) {
        dispatchError(message);
        return true;
    }

    return false;
}