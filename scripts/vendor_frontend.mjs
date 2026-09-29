import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const packages = join(root, 'node_modules');
const vendor = join(root, 'django_spire/core/static/django_spire/vendor');

const assets = [
  ['bootstrap/dist/js/bootstrap.bundle.min.js', 'bootstrap/bootstrap.bundle.min.js'],
  ['bootstrap/LICENSE', 'licenses/LICENSE-bootstrap'],
  ['bootstrap-icons/font/bootstrap-icons.min.css', 'bootstrap-icons/bootstrap-icons.min.css'],
  ['bootstrap-icons/font/fonts/bootstrap-icons.woff', 'bootstrap-icons/fonts/bootstrap-icons.woff'],
  ['bootstrap-icons/font/fonts/bootstrap-icons.woff2', 'bootstrap-icons/fonts/bootstrap-icons.woff2'],
  ['bootstrap-icons/LICENSE', 'licenses/LICENSE-bootstrap-icons'],
  ['echarts/dist/echarts.min.js', 'echarts/echarts.min.js'],
  ['echarts/LICENSE', 'licenses/LICENSE-echarts'],
  ['echarts/NOTICE', 'licenses/NOTICE-echarts'],
  ['echarts/licenses/LICENSE-d3', 'licenses/LICENSE-echarts-d3'],
  ['pulltorefreshjs/dist/index.umd.min.js', 'pulltorefreshjs/index.umd.min.js'],
  ['pulltorefreshjs/LICENSE.txt', 'licenses/LICENSE-pulltorefreshjs.txt'],
  ...['collapse', 'focus', 'intersect', 'mask', 'persist', 'sort'].map((name) => [
    `@alpinejs/${name}/dist/cdn.min.js`,
    `alpinejs/${name}.min.js`,
  ]),
];

for (const [source, destination] of assets) {
  const output = join(vendor, destination);
  mkdirSync(dirname(output), { recursive: true });
  copyFileSync(join(packages, source), output);
}
