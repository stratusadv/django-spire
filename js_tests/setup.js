import {GlobalRegistrator} from '@happy-dom/global-registrator'

GlobalRegistrator.register()

// Spire's scripts are plain files, not modules: each attaches to the global
// Spire object or registers with Alpine when alpine:init fires. Importing
// them here runs them once, as a page's script tags would, before Alpine
// starts. Alpine is imported only after happy-dom is registered, because it
// reads `document` and `window` when it loads.
const {default: Alpine} = await import('alpinejs')

globalThis.Alpine = Alpine

const SCRIPTS = '../django_spire/core/static/django_spire/js'

await import(`${SCRIPTS}/spire.js`)
await import(`${SCRIPTS}/notify.js`)
await import(`${SCRIPTS}/components/async_button.js`)
await import(`${SCRIPTS}/components/scroll.js`)

Alpine.start()
