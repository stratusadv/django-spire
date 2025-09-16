document.addEventListener('alpine:init', () => {
    Alpine.store('theme', {
        config: null,
        current: window.django_spire?.theme?.active || 'default-light',
        loading_config: false,

        async load_config() {
            if (this.config || this.loading_config) {
                return this.config;
            }

            this.loading_config = true;

            try {
                let response = await ajax_request(
                    'GET',
                    '/theme/ajax/get_config/'
                );

                if (response && response.data) {
                    this.config = response.data.data;
                }
            } catch (error) {
                console.error('Failed to load theme config:', error);
            }

            this.loading_config = false;
            return this.config;
        },

        parse(value) {
            let parts = value.split('-');
            let mode = parts.pop();
            let family = parts.join('-');
            return { family, mode };
        },

        build(family, mode) {
            return `${family}-${mode}`;
        },

        get_family_display_name(family) {
            if (this.config && this.config.families && this.config.families[family]) {
                return this.config.families[family].name;
            }

            return family;
        },

        get_current_theme() {
            let { family, mode } = this.parse(this.current);
            let path = window.django_spire?.theme?.path || '/static/django_spire/css/themes/{family}/app-{mode}.css';
            let family_name = this.get_family_display_name(family);

            return {
                family: family,
                family_name: family_name,
                mode: mode,
                value: this.build(family, mode),
                display: `${family_name} - ${mode.charAt(0).toUpperCase() + mode.slice(1)}`,
                is_dark: mode === 'dark',
                stylesheet: path.replace('{family}', family).replace('{mode}', mode)
            };
        },

        get_current_display_name() {
            let { family, mode } = this.parse(this.current);
            let family_name = this.get_family_display_name(family);
            return `${family_name} - ${mode.charAt(0).toUpperCase() + mode.slice(1)}`;
        },

        get_current_family_name() {
            let { family } = this.parse(this.current);
            return family;
        },

        async families() {
            let config = await this.load_config();

            if (!config || !config.families) {
                return [];
            }

            return Object.entries(config.families).map(([key, value]) => ({
                value: key,
                name: value.name
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

            if (window.django_spire && window.django_spire.theme) {
                window.django_spire.theme.active = theme.value;
            }
        },

        load_theme_css(family, mode) {
            let existing = document.querySelector('link[data-theme-css]');
            let path = window.django_spire?.theme?.path;

            if (!path) {
                console.error('Theme path is not defined');
                return;
            }

            if (!family || !mode) {
                console.error('Missing family or mode:', family, mode);
                return;
            }

            let href = path.replace('{family}', family).replace('{mode}', mode);
            let absolute = new URL(href, window.location).href;

            if (existing && existing.href === absolute) {
                return;
            }

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
            let { mode } = this.parse(this.current);
            let config = await this.load_config();

            if (config && config.families && config.families[family]) {
                if (!config.families[family].modes.includes(mode)) {
                    mode = config.families[family].modes[0];
                }
            }

            await this.set(this.build(family, mode));
        },

        async toggle() {
            let { family, mode } = this.parse(this.current);
            let newmode = mode === 'dark' ? 'light' : 'dark';
            await this.set(this.build(family, newmode));
        },

        is_family(family) {
            let { family: current } = this.parse(this.current);
            return current === family;
        },

        is_mode(mode) {
            let { mode: current } = this.parse(this.current);
            return current === mode;
        },

        init() {
            this.apply();
        }
    });
});
