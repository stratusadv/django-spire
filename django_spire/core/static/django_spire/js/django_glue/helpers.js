const UNEXPECTED_ERROR = 'An unexpected issue has occurred. Please refresh the page and try again.';

class GlueFetchHelper {
    /**
     * Performs a fetch request with django_glue_fetch and handles success/error callbacks
     * @param {string} url - Required: the endpoint URL
     * @param {Object} options - Configuration options
     * @param {Object} [options.payload] - Request payload data
     * @param {Function} [options.successHandler] - Callback on successful response
     * @param {Function} [options.errorHandler] - Callback on error response
     * @param {string} [options.method='POST'] - HTTP method (GET, POST, PUT, DELETE, etc.)
     * @param {string} [options.contentType='application/json'] - Content-Type header
     * @param {string} [options.responseType='json'] - Response type (json, text, blob)
     * @param {Object} [options.headerOptions={}] - Additional custom headers
     * @param {string} [options.defaultErrorMessage=UNEXPECTED_ERROR] - Default error message
     * @returns {Promise<{success: boolean, response?: Object, error?: Error}>}
     */
    static async tryGlueFetch(url,{
        payload = {},
        successHandler,
        errorHandler,
        method = 'POST',
        contentType = 'application/json',
        responseType = 'json',
        headerOptions = {},
        defaultErrorMessage = UNEXPECTED_ERROR,
    } = {}) {
        if (!url) {
            throw new Error('No URL was provided.');
        }

        try {
            const response = await django_glue_fetch(url, {
                payload,
                method,
                content_type: contentType,
                response_type: responseType,
                header_options: headerOptions,
            });

            const isError = tryDispatchResponseError(response, defaultErrorMessage);

            if (!isError && successHandler) {
                successHandler(response);
            }

            if (isError && errorHandler) {
                errorHandler(response);
            }

            return {success: !isError, response};
        } catch (e) {
            dispatchError(defaultErrorMessage);
            console.error(e);
            return {success: false, error: e};
        }
    }
}


class GlueObjectHelper {

}


class GlueQuerySetHelper {

}