document.addEventListener('alpine:init', () => {
    Alpine.store('theme', {
        available: [
            { name: 'Ayu Light', value: 'ayu-light', family: 'ayu', mode: 'light' },
            { name: 'Ayu Dark', value: 'ayu-dark', family: 'ayu', mode: 'dark' },
            { name: 'Catppuccin Light', value: 'catppuccin-light', family: 'catppuccin', mode: 'light' },
            { name: 'Catppuccin Dark', value: 'catppuccin-dark', family: 'catppuccin', mode: 'dark' },
            { name: 'Default Light', value: 'default-light', family: 'default', mode: 'light' },
            { name: 'Default Dark', value: 'default-dark', family: 'default', mode: 'dark' },
            { name: 'Dracula Light', value: 'dracula-light', family: 'dracula', mode: 'light' },
            { name: 'Dracula Dark', value: 'dracula-dark', family: 'dracula', mode: 'dark' },
            { name: 'Gruvbox Light', value: 'gruvbox-light', family: 'gruvbox', mode: 'light' },
            { name: 'Gruvbox Dark', value: 'gruvbox-dark', family: 'gruvbox', mode: 'dark' },
            { name: 'Material Light', value: 'material-light', family: 'material', mode: 'light' },
            { name: 'Material Dark', value: 'material-dark', family: 'material', mode: 'dark' },
            { name: 'Nord Light', value: 'nord-light', family: 'nord', mode: 'light' },
            { name: 'Nord Dark', value: 'nord-dark', family: 'nord', mode: 'dark' },
            { name: 'Oceanic Next Light', value: 'oceanic-next-light', family: 'oceanic-next', mode: 'light' },
            { name: 'Oceanic Next Dark', value: 'oceanic-next-dark', family: 'oceanic-next', mode: 'dark' },
            { name: 'One Dark Pro Light', value: 'one-dark-light', family: 'one-dark', mode: 'light' },
            { name: 'One Dark Pro Dark', value: 'one-dark-dark', family: 'one-dark', mode: 'dark' },
            { name: 'Palenight Light', value: 'palenight-light', family: 'palenight', mode: 'light' },
            { name: 'Palenight Dark', value: 'palenight-dark', family: 'palenight', mode: 'dark' },
            { name: 'Rose Pine Light', value: 'rose-pine-light', family: 'rose-pine', mode: 'light' },
            { name: 'Rose Pine Dark', value: 'rose-pine-dark', family: 'rose-pine', mode: 'dark' },
            { name: 'Synthwave Light', value: 'synthwave-light', family: 'synthwave', mode: 'light' },
            { name: 'Synthwave Dark', value: 'synthwave-dark', family: 'synthwave', mode: 'dark' },
            { name: 'Tokyo Night Light', value: 'tokyo-night-light', family: 'tokyo-night', mode: 'light' },
            { name: 'Tokyo Night Dark', value: 'tokyo-night-dark', family: 'tokyo-night', mode: 'dark' }
        ],

        families: [
            { name: 'Ayu', value: 'ayu' },
            { name: 'Catppuccin', value: 'catppuccin' },
            { name: 'Default', value: 'default' },
            { name: 'Dracula', value: 'dracula' },
            { name: 'Gruvbox', value: 'gruvbox' },
            { name: 'Material', value: 'material' },
            { name: 'Nord', value: 'nord' },
            { name: 'Oceanic Next', value: 'oceanic-next' },
            { name: 'One Dark Pro', value: 'one-dark' },
            { name: 'Palenight', value: 'palenight' },
            { name: 'Rose Pine', value: 'rose-pine' },
            { name: 'Synthwave', value: 'synthwave' },
            { name: 'Tokyo Night', value: 'tokyo-night' }
        ],

        current: window.app_theme || window.default_theme || 'default-light',

        get_current_theme() {
            return this.available.find(theme => theme.value === this.current) || this.available[0];
        },

        get_current_family_name() {
            let current = this.get_current_theme();
            let family = this.families.find(f => f.value === current.family);
            return family ? family.name : 'Unknown';
        },

        get_current_display_name() {
            let current = this.get_current_theme();
            let family = this.families.find(f => f.value === current.family);
            let family_name = family ? family.name : 'Unknown';
            let mode_name = current.mode.charAt(0).toUpperCase() + current.mode.slice(1);
            return `${family_name} - ${mode_name}`;
        },

        apply() {
            let theme = this.get_current_theme();

            if (theme.mode === 'dark') {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }

            document.documentElement.setAttribute('data-theme-family', theme.family);
            this.load_theme_css(theme.family, theme.mode);
        },

        load_theme_css(family, mode) {
            let existing_link = document.querySelector('link[data-theme-css]');
            let href = `/static/django_spire/css/themes/${family}/app-${mode}.css`;

            let link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.setAttribute('data-theme-css', 'true');

            link.onload = () => {
                if (existing_link) {
                    existing_link.remove();
                }
            };

            document.head.appendChild(link);
        },

        async persist_to_server(theme) {
            await ajax_request(
                'POST',
                '/theme/ajax/set_theme/',
                { theme: theme }
            );
        },

        toggle() {
            let current = this.get_current_theme();

            let mode = current.mode === 'dark' ? 'light' : 'dark';
            let value = current.family + '-' + mode;
            let theme = this.available.find(t => t.value === value);

            if (theme) {
                this.set(theme.value);
            }
        },

        set_family(family) {
            let current = this.get_current_theme();
            let value = family + '-' + current.mode;
            let theme = this.available.find(t => t.value === value);

            if (theme) {
                this.set(theme.value);
            }
        },

        async set(theme) {
            this.current = theme;
            this.apply();

            await this.persist_to_server(theme);
        },

        is_family(family) {
            return this.get_current_theme().family === family;
        },

        is_mode(mode) {
            return this.get_current_theme().mode === mode;
        }
    });
});
