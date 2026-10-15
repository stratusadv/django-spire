document.addEventListener('alpine:init', () => {
    Alpine.data('sideNavigation', () => ({
        collapsed: JSON.parse(localStorage.getItem('side_nav_collapsed') || 'false'),
        show_top_fade: false,
        show_bottom_fade: false,

        init() {
            this.$nextTick(() => {
                this.check_scroll();
                window.addEventListener('resize', () => this.check_scroll());
            });
        },

        check_scroll() {
            let element = this.$refs.scroll_container;
            let has_scroll = element.scrollHeight > element.clientHeight;
            let is_at_top = element.scrollTop <= 20;
            let is_at_bottom = element.scrollHeight - element.scrollTop <= element.clientHeight + 20;
            this.show_top_fade = has_scroll && !is_at_top;
            this.show_bottom_fade = has_scroll && !is_at_bottom;
        },

        save_scroll() {
            localStorage.setItem('side_nav_scroll', this.$refs.scroll_container.scrollTop);
        },

        toggle_collapse() {
            this.collapsed = !this.collapsed;
            localStorage.setItem('side_nav_collapsed', JSON.stringify(this.collapsed));
            document.documentElement.style.setProperty(
                '--side-navigation-width',
                this.collapsed ? '68px' : '240px'
            );

            if (this.collapsed) {
                document.documentElement.classList.add('side-nav-collapsed');
            } else {
                document.documentElement.classList.remove('side-nav-collapsed');
            }

            this.$nextTick(() => this.check_scroll());
        }
    }));
});

document.addEventListener('alpine:init', () => {
    Alpine.data('sideNavAccordion', () => ({
        show_accordion: false,

        init() {
            this.show_accordion = this.$el.classList.contains('side-nav-accordion-open');
        },

        toggle() {
            this.show_accordion = !this.show_accordion;
            this.$root.classList.toggle('side-nav-accordion-open', this.show_accordion);
        }
    }));
});

document.addEventListener('DOMContentLoaded', () => {
    let container = document.querySelector('[data-side-navigation-scroll]');
    let position = parseFloat(localStorage.getItem('side_nav_scroll') || '0');

    if (container && position > 0) {
        container.scrollTop = position;
    }
});
