// The libraries every spire page uses, at the versions package.json pins.
// Bootstrap and PullToRefresh stay globals, as their CDN builds made them.
import collapse from '@alpinejs/collapse';
import focus from '@alpinejs/focus';
import intersect from '@alpinejs/intersect';
import mask from '@alpinejs/mask';
import persist from '@alpinejs/persist';
import sort from '@alpinejs/sort';
import bootstrap from 'bootstrap/dist/js/bootstrap.bundle.js';
import PullToRefresh from 'pulltorefreshjs';

window.bootstrap = bootstrap;
window.PullToRefresh = PullToRefresh;

// Glue owns Alpine and starts it; the plugins register with it first.
document.addEventListener('alpine:init', () => {
    for (const plugin of [collapse, focus, intersect, mask, persist, sort]) {
        window.Alpine.plugin(plugin);
    }
});
