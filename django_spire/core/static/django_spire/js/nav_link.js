document.addEventListener('alpine:init', () => {
    Alpine.data('navLink', (currentPath, linkPath) => ({
        current_path: currentPath,
        link_path: linkPath,

        is_active() {
            if (!this.link_path) {
                return false;
            }

            return this.current_path === this.link_path
                || this.current_path.startsWith(this.link_path + '/');
        },

        redirect() {
            const SPINNER_DELAY = 1000;
            const url = this.link_path;

            this.$dispatch('nav-redirect', { path: url });

            let spinnerTimer = setTimeout(() => {
                Spire.ui.toggleLoadingSpinner();
            }, SPINNER_DELAY);

            fetch(url, { method: 'GET', headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(() => {
                    clearTimeout(spinnerTimer);
                    window.location = url;
                })
                .catch(() => {
                    clearTimeout(spinnerTimer);
                    window.location = url;
                });
        }
    }));
});
