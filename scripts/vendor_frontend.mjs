import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const packages = join(root, 'node_modules');
const vendor = join(root, 'test_project/vendor');

// What pages still load from a CDN; the browser tests serve these copies instead.
// The libraries in core's bundle come from node_modules when it is built.
const assets = [
  ['bootstrap-icons/font/bootstrap-icons.min.css', 'bootstrap-icons/bootstrap-icons.min.css'],
  ['bootstrap-icons/font/fonts/bootstrap-icons.woff', 'bootstrap-icons/fonts/bootstrap-icons.woff'],
  ['bootstrap-icons/font/fonts/bootstrap-icons.woff2', 'bootstrap-icons/fonts/bootstrap-icons.woff2'],
  ['bootstrap-icons/LICENSE', 'licenses/LICENSE-bootstrap-icons'],
  ['echarts/dist/echarts.min.js', 'echarts/echarts.min.js'],
  ['echarts/LICENSE', 'licenses/LICENSE-echarts'],
  ['echarts/NOTICE', 'licenses/NOTICE-echarts'],
  ['echarts/licenses/LICENSE-d3', 'licenses/LICENSE-echarts-d3'],
];

for (const [source, destination] of assets) {
  const output = join(vendor, destination);
  mkdirSync(dirname(output), { recursive: true });
  copyFileSync(join(packages, source), output);
}
