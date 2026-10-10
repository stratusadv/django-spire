import {afterEach, beforeEach, describe, expect, test} from 'bun:test'

let notifications

function record(event) {
    notifications.push(event.detail)
}

beforeEach(() => {
    notifications = []
    window.addEventListener('notify', record)
})

afterEach(() => {
    window.removeEventListener('notify', record)
})

describe('Spire.notify.glueError', () => {
    const GONE = 'That item no longer exists.'
    const DENIED = 'You do not have permission to do that.'
    const FAILED = 'Something went wrong. Please try again.'

    test.each([
        ['a missing row, by code', {code: 'model_instance_not_found'}, GONE],
        ['a missing row, by status', {status: 404}, GONE],
        ['a denial, by code', {code: 'not_authorized'}, DENIED],
        ['a denial, by status', {status: 403}, DENIED],
        ['a server error', {code: 'bound_attribute_call_error', status: 500}, FAILED],
        ['an error with neither a code nor a status', new Error('boom'), FAILED],
        ['nothing at all', undefined, FAILED],
    ])('tells the user about %s', (_case, error, message) => {
        Spire.notify.glueError(error)

        expect(notifications).toEqual([{type: 'error', message}])
    })

    test('never shows the message the server sent', () => {
        Spire.notify.glueError({
            code: 'model_instance_not_found',
            message: 'test_project.Task with pk=5 does not exist.',
        })

        expect(notifications[0].message).not.toContain('pk=5')
    })
})

describe('Spire.notify.dispatch', () => {
    test('refuses a type it does not know', () => {
        expect(() => Spire.notify.dispatch({type: 'shout', message: 'Hello'})).toThrow(
            'Dispatch message type invalid: shout',
        )
        expect(notifications).toEqual([])
    })
})
