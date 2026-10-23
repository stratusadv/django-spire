// Puts markup on the page and waits for Alpine to initialise it.
export async function mount(html) {
    document.body.innerHTML = html
    await settle()
}

// Lets pending promise callbacks and Alpine's reactive updates run.
export async function settle() {
    await new Promise(resolve => setTimeout(resolve, 0))
}

// A promise a test settles by hand, to hold a call in flight.
export function deferred() {
    let resolve
    let reject
    const promise = new Promise((resolvePromise, rejectPromise) => {
        resolve = resolvePromise
        reject = rejectPromise
    })

    return {promise, resolve, reject}
}
