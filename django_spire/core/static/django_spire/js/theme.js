document.addEventListener('alpine:init', () => {
    Alpine.store('theme', {
        config: JSON.parse(document.getElementById('theme-config').textContent),
        current: window.app_theme || window.default_theme || 'default-light',

        parse(value) {
            let parts = value.split(this.config.separator);
            let mode = parts.pop();
            let family = parts.join(this.config.separator);

            if (!this.config.families[family]) {
                family = this.config.default_family;
                mode = this.config.default_mode;
            }

            if (!this.config.families[family].modes.includes(mode)) {
                mode = this.config.default_mode;
            }

            return { family, mode };
        },

        build(family, mode) {
            return `${family}${this.config.separator}${mode}`;
        },

        get_current_theme() {
            let { family, mode } = this.parse(this.current);
            let family_config = this.config.families[family];

            return {
                family: family,
                family_name: family_config.name,
                mode: mode,
                value: this.build(family, mode),
                display: `${family_config.name} - ${mode.charAt(0).toUpperCase() + mode.slice(1)}`,
                is_dark: mode === 'dark',
                stylesheet: window.app_theme_path.replace('{family}', family).replace('{mode}', mode)
            };
        },

        get_current_display_name() {
            return this.get_current_theme().display;
        },

        get_current_family_name() {
            return this.get_current_theme().family_name;
        },

        families() {
            return Object.entries(this.config.families).map(([key, config]) => ({
                value: key,
                name: config.name
            }));
        },

        apply() {
            let theme = this.get_current_theme();

            if (theme.is_dark) {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }

            document.documentElement.setAttribute('data-theme-family', theme.family);
            this.load_theme_css(theme.family, theme.mode);
        },

        load_theme_css(family, mode) {
            let existing = document.querySelector('link[data-theme-css]');

            if (!window.app_theme_path) {
                console.error('app_theme_path is not defined');
                return;
            }

            if (!family || !mode) {
                console.error('Missing family or mode:', family, mode);
                return;
            }

            let href = window.app_theme_path.replace('{family}', family).replace('{mode}', mode);

            let link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.setAttribute('data-theme-css', 'true');

            link.onload = () => {
                if (existing) {
                    existing.remove();
                }
            };

            document.head.appendChild(link);
        },

        async persist_to_server(value) {
            await ajax_request(
                'POST',
                '/theme/ajax/set_theme/',
                { theme: value }
            );
        },

        async set(value) {
            this.current = value;
            this.apply();
            await this.persist_to_server(value);
        },

        async set_family(family) {
            let current = this.get_current_theme();
            let mode = current.mode;

            if (!this.config.families[family].modes.includes(mode)) {
                mode = this.config.families[family].modes[0];
            }

            await this.set(this.build(family, mode));
        },

        async toggle() {
            let current = this.get_current_theme();
            let mode = current.is_dark ? 'light' : 'dark';
            await this.set(this.build(current.family, mode));
        },

        is_family(family) {
            return this.get_current_theme().family === family;
        },

        is_mode(mode) {
            return this.get_current_theme().mode === mode;
        }
    });
});
