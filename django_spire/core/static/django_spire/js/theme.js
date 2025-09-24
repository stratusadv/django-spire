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
                    '/django_spire/theme/json/get_config/'
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

            if (!document.querySelector('link[data-input-css]')) {
                let link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = '/static/django_spire/css/themes/input.css';
                link.setAttribute('data-input-css', 'true');

                document.head.appendChild(link);
            }

            setTimeout(() => this.apply_input_icon_theme(), 100);
        },

        apply_input_icon_theme() {
            // This is a fix for a Chromium-based browser. We have to dynamically
            // target the input field icon, otherwise it won't be styled properly.

            let text_color = getComputedStyle(document.documentElement).getPropertyValue('--app-default-text-color').trim();

            if (!text_color) return;

            let hex = text_color.replace('#', '%23');
            let style_id = 'calendar-icon-theme';
            let existing = document.getElementById(style_id);

            if (existing) {
                existing.remove();
            }

            let calendar_svg = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="${hex}" stroke-width="1.5" viewBox="0 0 16 16"><rect x="2" y="3" width="12" height="11" rx="1"/><path d="M2 6h12M5 1v3M11 1v3"/><circle cx="5" cy="9" r="0.5" fill="${hex}"/><circle cx="8" cy="9" r="0.5" fill="${hex}"/><circle cx="11" cy="9" r="0.5" fill="${hex}"/><circle cx="5" cy="12" r="0.5" fill="${hex}"/><circle cx="8" cy="12" r="0.5" fill="${hex}"/><circle cx="11" cy="12" r="0.5" fill="${hex}"/></svg>`;
            let clock_svg = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="${hex}"><path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/><path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/></svg>`;

            let style = document.createElement('style');
            style.id = style_id;

            style.textContent = `
                input[type="datetime-local"]::-webkit-calendar-picker-indicator,
                input[type="date"]::-webkit-calendar-picker-indicator,
                input[type="week"]::-webkit-calendar-picker-indicator,
                input[type="month"]::-webkit-calendar-picker-indicator {
                    background-image: url('${calendar_svg}');
                }

                input[type="time"]::-webkit-calendar-picker-indicator {
                    background-image: url('${clock_svg}');
                }
            `;
            document.head.appendChild(style);
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

                this.apply_input_icon_theme();
            };

            document.head.appendChild(link);
        },

        async persist_to_server(value) {
            await ajax_request(
                'POST',
                '/django_spire/theme/json/set_theme/',
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
