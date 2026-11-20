// Builds each spire app's JavaScript into the bundle its pages load.
//
// An app's entry is static/<app name, dots as slashes>/index.js, and its
// bundle is the bundle.js beside it: django_spire.notification builds
// django_spire/notification/static/django_spire/notification/bundle.js.
import { readdirSync, readFileSync, existsSync, writeFileSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const APP_NAME = /^\s*name\s*=\s*['"]([\w.]+)['"]/m;

export function findEntries() {
  const entries = [];

  const visit = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      if (!entry.isDirectory() || entry.name === 'static' || entry.name === 'templates' || entry.name.startsWith('_')) {
        continue;
      }

      const path = join(directory, entry.name);
      const apps = join(path, 'apps.py');
      const name = existsSync(apps) && readFileSync(apps, 'utf8').match(APP_NAME)?.[1];
      const index = name && join(path, 'static', ...name.split('.'), 'index.js');

      if (index && existsSync(index)) {
        entries.push(index);
      }

      visit(path);
    }
  };

  visit(join(root, 'django_spire'));

  return entries.sort();
}

// The bundle and its source map, as text, for one entry.
export async function buildBundle(entry) {
  const result = await Bun.build({
    entrypoints: [entry],
    target: 'browser',
    format: 'iife',
    minify: true,
    sourcemap: 'linked',
    naming: 'bundle.js',
    root: dirname(entry),
  });

  if (!result.success) {
    throw new AggregateError(result.logs, `${relative(root, entry)} did not build`);
  }

  const output = (kind) => result.outputs.find((artifact) => artifact.kind === kind).text();

  return { bundle: await output('entry-point'), map: await output('sourcemap') };
}

if (import.meta.main) {
  for (const entry of findEntries()) {
    const { bundle, map } = await buildBundle(entry);
    const directory = dirname(entry);

    writeFileSync(join(directory, 'bundle.js'), bundle);
    writeFileSync(join(directory, 'bundle.js.map'), map);
    console.log(`${relative(root, join(directory, 'bundle.js'))}: ${bundle.length} bytes`);
  }
}
