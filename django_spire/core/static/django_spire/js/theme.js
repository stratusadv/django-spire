document.addEventListener('alpine:init', () => {
    Alpine.store('theme', {
        storage_key: 'django_spire-theme-mode',
        current: 'light',

        toggle() {
            this.current = this.current === 'dark' ? 'light' : 'dark';
            this.apply();
            this.persist();
        },

        apply() {
            if (this.current === 'dark') {
                document.documentElement.setAttribute('data-bs-theme', 'dark');
            } else {
                document.documentElement.removeAttribute('data-bs-theme');
            }

            // setTimeout(() => this.apply_input_icon_theme(), 100);
        },

        persist() {
            localStorage.setItem(this.storage_key, this.current);
        },

        // apply_input_icon_theme() {
        //     let text_color = getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color').trim();
        //
        //     if (!text_color) return;
        //
        //     let hex = text_color.replace('#', '%23');
        //     let style_id = 'calendar-icon-theme';
        //     let existing = document.getElementById(style_id);
        //
        //     if (existing) {
        //         existing.remove();
        //     }
        //
        //     let calendar_svg = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="${hex}" stroke-width="1.5" viewBox="0 0 16 16"><rect x="2" y="3" width="12" height="11" rx="1"/><path d="M2 6h12M5 1v3M11 1v3"/><circle cx="5" cy="9" r="0.5" fill="${hex}"/><circle cx="8" cy="9" r="0.5" fill="${hex}"/><circle cx="11" cy="9" r="0.5" fill="${hex}"/><circle cx="5" cy="12" r="0.5" fill="${hex}"/><circle cx="8" cy="12" r="0.5" fill="${hex}"/><circle cx="11" cy="12" r="0.5" fill="${hex}"/></svg>`;
        //     let clock_svg = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="${hex}"><path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/><path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/></svg>`;
        //
        //     let style = document.createElement('style');
        //     style.id = style_id;
        //
        //     style.textContent = `
        //         input[type="datetime-local"]::-webkit-calendar-picker-indicator,
        //         input[type="date"]::-webkit-calendar-picker-indicator,
        //         input[type="week"]::-webkit-calendar-picker-indicator,
        //         input[type="month"]::-webkit-calendar-picker-indicator {
        //             background-image: url('${calendar_svg}');
        //         }
        //
        //         input[type="time"]::-webkit-calendar-picker-indicator {
        //             background-image: url('${clock_svg}');
        //         }
        //     `;
        //     document.head.appendChild(style);
        // },

        init() {
            this.current = localStorage.getItem(this.storage_key) ||
                window.django_spire?.theme?.mode || 'light';
            this.apply();
        }
    });
});

window.get_echarts_theme = function() {
    let styles = getComputedStyle(document.documentElement);
    let is_dark = document.documentElement.getAttribute('data-bs-theme') === 'dark';

    return {
        bg: styles.getPropertyValue('--bs-body-bg').trim(),
        border: styles.getPropertyValue('--bs-border-color').trim(),
        danger: styles.getPropertyValue('--bs-danger').trim(),
        is_dark: is_dark,
        layer_two: styles.getPropertyValue('--bs-tertiary-bg').trim(),
        primary: styles.getPropertyValue('--bs-primary').trim(),
        primary_dark: styles.getPropertyValue('--bs-primary').trim(),
        secondary: styles.getPropertyValue('--bs-secondary').trim(),
        secondary_dark: styles.getPropertyValue('--bs-secondary').trim(),
        success: styles.getPropertyValue('--bs-success').trim(),
        text: styles.getPropertyValue('--bs-body-color').trim(),
        warning: styles.getPropertyValue('--bs-warning').trim(),
    };
};