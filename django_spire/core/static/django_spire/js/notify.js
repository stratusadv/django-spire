window.Spire = window.Spire || {};

const NOTIFICATION_TYPES = {
    error: 'error',
    warning: 'warning',
    info: 'info',
    success: 'success',
};

const NOTIFY_EVENT = 'notify';
const VALID_NOTIFY_TYPES = Object.values(NOTIFICATION_TYPES);

Spire.notify = {
    /**
     * @param {object} options
     * @param {string} options.type - 'error', 'warning', 'info', 'success'
     * @param {string} options.message
     */
    dispatch({type, message}) {
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
    },

    /**
     * @param {string} message
     */
    error(message) {
        Spire.notify.dispatch({type: NOTIFICATION_TYPES.error, message: message});
    },

    /**
     * @param {string} message
     */
    info(message) {
        Spire.notify.dispatch({type: NOTIFICATION_TYPES.info, message: message});
    },

    /**
     * @param {string} message
     */
    success(message) {
        Spire.notify.dispatch({type: NOTIFICATION_TYPES.success, message: message});
    },

    /**
     * @param {string} message
     */
    warning(message) {
        Spire.notify.dispatch({type: NOTIFICATION_TYPES.warning, message: message});
    },

    /**
     * @param {object|null} response - http response object
     * @param {string} defaultMessage - default error message if one is not supplied in the response
     * @returns {boolean} - true if error was dispatched
     */
    tryResponseError(response, defaultMessage) {
        let message = response == null ? defaultMessage : response.message;
        let type = response == null ? NOTIFICATION_TYPES.error : response.type;

        if (response == null || type === NOTIFICATION_TYPES.error) {
            Spire.notify.error(message);
            return true;
        }

        return false;
    }
};