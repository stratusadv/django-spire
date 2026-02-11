const UNEXPECTED_ERROR = 'An unexpected issue has occurred. Please refresh the page and try again.';


class GlueRetryHelper {
    /**
     * Internal helper that implements retry logic for async operations
     * @param {Function} asyncFn - The async operation to execute
     * @param {number} maxRetries - Max number of retries before returning error
     * @param {Function} errorHelper - Function to be called following an error
     * @param {number} delayMs - Delay between retry calls
     * @returns {Promise<Object> | null}
     */
    static async executeWithRetry(
        asyncFn, maxRetries = 1, errorHelper = null, delayMs = 100) {
        let lastError = null;
        let attempt = 0;

        while (attempt < maxRetries) {
            try {
                return await asyncFn();
            } catch (error) {
                lastError = error;
                attempt++;

                if (errorHelper) {
                    errorHelper();
                }

                if (attempt < maxRetries) {
                    await new Promise(resolve => setTimeout(resolve, delayMs));
                }
            }
        }

        dispatchError(UNEXPECTED_ERROR);
    }
}


class GlueFetchHelper
    extends GlueRetryHelper {
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
     * @param {number} [options.maxRetries=1] - Max number of retries before returning error
     * @param {Function} [options.errorHelper] - Function to be called following an error
     * @param {number} [options.delayMs=100] - Delay between retry calls
     * @returns {Promise<{success: boolean, response?: Object, error?: Error}>}
     */
    static async tryGlueFetch(url, {
        payload = {},
        successHandler,
        errorHandler,
        method = 'POST',
        contentType = 'application/json',
        responseType = 'json',
        headerOptions = {},
        defaultErrorMessage = UNEXPECTED_ERROR,
        maxRetries = 1,
        errorHelper = null,
        delayMs = 100,
    } = {}) {
        if (!url) {
            throw new Error('No URL was provided.');
        }

        try {
            const response = await this.executeWithRetry(
                () => django_glue_fetch(url, {
                    payload,
                    method,
                    content_type: contentType,
                    response_type: responseType,
                    header_options: headerOptions,
                }),
                maxRetries,
                errorHelper,
                delayMs,
            );

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


class GlueObjectHelper
    extends GlueRetryHelper {
    /**
     * @param glueObject {ModelObjectGlue}
     * @param maxRetries {number} - Max number of retries before returning error
     * @param errorHelper {Function} - Function to be called following an error
     * @param delayMs {number} - Delay between retry calls
     * @returns {Promise<{success: boolean}|{success: boolean, error: null}>}
     */
    static async tryGlueGet(
        glueObject,
        maxRetries = 1,
        errorHelper = null,
        delayMs = 100,
    ) {
        return this.executeWithRetry(
            () => glueObject.get(),
            maxRetries,
            errorHelper,
            delayMs,
        );
    }
}


class GlueQuerySetHelper
    extends GlueRetryHelper {
    /**
     * Fetches all objects from the queryset with retry logic
     * @param {QuerySetGlue} glueQuerySet
     * @param {number} maxRetries - Max number of retries before returning error
     * @param {Function} errorHelper - Function to be called following an error
     * @param {number} delayMs - Delay between retry calls
     * @returns {Promise<Array>}
     */
    static async tryAll(
        glueQuerySet, maxRetries = 1, errorHelper = null, delayMs = 100) {
        return this.executeWithRetry(
            () => glueQuerySet.all(),
            maxRetries,
            errorHelper,
            delayMs,
        );
    }

    /**
     * Deletes an object by id with retry logic
     * @param {QuerySetGlue} glueQuerySet
     * @param {*} id - The id of the object to delete
     * @param {number} maxRetries - Max number of retries before returning error
     * @param {Function} errorHelper - Function to be called following an error
     * @param {number} delayMs - Delay between retry calls
     * @returns {Promise<void>}
     */
    static async tryDelete(
        glueQuerySet, id, maxRetries = 1, errorHelper = null, delayMs = 100) {
        return this.executeWithRetry(
            () => glueQuerySet.delete(id),
            maxRetries,
            errorHelper,
            delayMs,
        );
    }

    /**
     * Filters objects with retry logic
     * @param {QuerySetGlue} glueQuerySet
     * @param {Object} filterParams - Filter parameters
     * @param {number} maxRetries - Max number of retries before returning error
     * @param {Function} errorHelper - Function to be called following an error
     * @param {number} delayMs - Delay between retry calls
     * @returns {Promise<Array>}
     */
    static async tryFilter(
        glueQuerySet, filterParams = {}, maxRetries = 1, errorHelper = null,
        delayMs = 100,
    ) {
        return this.executeWithRetry(
            () => glueQuerySet.filter(filterParams),
            maxRetries,
            errorHelper,
            delayMs,
        );
    }

    /**
     * Gets a single object by id with retry logic
     * @param {QuerySetGlue} glueQuerySet
     * @param {*} id - The id of the object to retrieve
     * @param {number} maxRetries - Max number of retries before returning error
     * @param {Function} errorHelper - Function to be called following an error
     * @param {number} delayMs - Delay between retry calls
     * @returns {Promise<ModelObjectGlue>}
     */
    static async tryGet(
        glueQuerySet, id, maxRetries = 1, errorHelper = null, delayMs = 100) {
        return this.executeWithRetry(
            () => glueQuerySet.get(id),
            maxRetries,
            errorHelper,
            delayMs,
        );
    }

    /**
     * Calls a method on the queryset with retry logic
     * @param {QuerySetGlue} glueQuerySet
     * @param {*} id - The id of the object
     * @param {string} method - The method name to call
     * @param {Object} kwargs - Keyword arguments for the method
     * @param {number} maxRetries - Max number of retries before returning error
     * @param {Function} errorHelper - Function to be called following an error
     * @param {number} delayMs - Delay between retry calls
     * @returns {Promise<*>}
     */
    static async tryMethod(
        glueQuerySet, id, method, kwargs = {}, maxRetries = 1, errorHelper = null,
        delayMs = 100,
    ) {
        return this.executeWithRetry(
            () => glueQuerySet.method(id, method, kwargs),
            maxRetries,
            errorHelper,
            delayMs,
        );
    }

    /**
     * Gets a null/empty object from the queryset with retry logic
     * @param {QuerySetGlue} glueQuerySet
     * @param {number} maxRetries - Max number of retries before returning error
     * @param {Function} errorHelper - Function to be called following an error
     * @param {number} delayMs - Delay between retry calls
     * @returns {Promise<ModelObjectGlue>}
     */
    static async tryNullObject(
        glueQuerySet, maxRetries = 1, errorHelper = null, delayMs = 100) {
        return this.executeWithRetry(
            () => glueQuerySet.null_object(),
            maxRetries,
            errorHelper,
            delayMs,
        );
    }

    /**
     * Converts queryset to choices with retry logic
     * @param {QuerySetGlue} glueQuerySet
     * @param {Object} filterParams - Filter parameters
     * @param {number} maxRetries - Max number of retries before returning error
     * @param {Function} errorHelper - Function to be called following an error
     * @param {number} delayMs - Delay between retry calls
     * @returns {Promise<Array>}
     */
    static async tryToChoices(
        glueQuerySet, filterParams = {}, maxRetries = 1, errorHelper = null,
        delayMs = 100,
    ) {
        return this.executeWithRetry(
            () => glueQuerySet.to_choices(filterParams),
            maxRetries,
            errorHelper,
            delayMs,
        );
    }

    /**
     * Updates objects in the queryset with retry logic
     * @param {QuerySetGlue} glueQuerySet
     * @param {ModelObjectGlue} queryModelObject - The model object with updated data
     * @param {string|null} field - Specific field to update, or null to update all fields
     * @param {number} maxRetries - Max number of retries before returning error
     * @param {Function} errorHelper - Function to be called following an error
     * @param {number} delayMs - Delay between retry calls
     * @returns {Promise<void>}
     */
    static async tryUpdate(
        glueQuerySet, queryModelObject, field = null, maxRetries = 1,
        errorHelper = null, delayMs = 100,
    ) {
        return this.executeWithRetry(
            () => glueQuerySet.update(queryModelObject, field),
            maxRetries,
            errorHelper,
            delayMs,
        );
    }
}