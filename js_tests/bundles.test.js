import {describe, expect, test} from 'bun:test'
import {readFileSync} from 'node:fs'
import {dirname, join, relative} from 'node:path'

import {buildBundle, findEntries} from '../scripts/build_javascript.mjs'

const root = join(import.meta.dir, '..')

describe('app bundles', () => {
    test('are found by each app name', () => {
        expect(findEntries().map((entry) => relative(root, entry))).toEqual([
            'django_spire/core/static/django_spire/core/index.js',
            'django_spire/file/static/django_spire/file/index.js',
            'django_spire/notification/static/django_spire/notification/index.js',
        ])
    })

    // A failure means a source changed without a rebuild: run `just build-js`.
    for (const entry of findEntries()) {
        test(`${relative(root, dirname(entry))}/bundle.js is current`, async () => {
            const {bundle, map} = await buildBundle(entry)

            expect(readFileSync(join(dirname(entry), 'bundle.js'), 'utf8')).toBe(bundle)
            expect(readFileSync(join(dirname(entry), 'bundle.js.map'), 'utf8')).toBe(map)
        })
    }
})
