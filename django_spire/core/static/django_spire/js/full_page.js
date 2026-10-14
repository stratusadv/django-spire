document.addEventListener('alpine:init', () => {
    Alpine.data('fullPage', () => ({
        info_nav_max_width: 600,
        info_nav_min_width: 200,
        info_nav_width: 400,
        is_mobile: false,
        is_narrow_viewport: false,
        is_resizing_info: false,
        is_resizing_sub: false,
        resize_start_width: 0,
        resize_start_x: 0,
        show_info_nav: false,
        show_sub_nav: false,
        sub_nav_has_been_resized: false,
        sub_nav_max_width: 600,
        sub_nav_min_width: 300,
        sub_nav_width: 300,

        is_touch_device() {
            return window.matchMedia('(pointer: coarse)').matches || 'ontouchstart' in window;
        },

        update_command_bar_height() {
            let sticky_header = this.$refs.sticky_header;
            let top_nav_height = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--top-navigation-height'));
            let command_bar_height = sticky_header.offsetHeight - top_nav_height;

            document.documentElement.style.setProperty(
                '--app-command-bar-height',
                Math.max(0, command_bar_height) + 'px'
            );
        },

        update_viewport_state() {
            const was_narrow = this.is_narrow_viewport;
            const is_now_narrow = window.innerWidth < 992;
            this.is_narrow_viewport = is_now_narrow;
            this.is_mobile = this.is_touch_device();

            if (!was_narrow && is_now_narrow) {
                this.show_sub_nav = false;
                this.show_info_nav = false;
            }

            if (was_narrow && !is_now_narrow) {
                this.$nextTick(() => {
                    this.show_sub_nav = false;
                    this.show_info_nav = false;
                });
            }

            if (!this.is_narrow_viewport) {
                this.show_info_nav = false;
            }
        },

        init() {
            this.is_mobile = this.is_touch_device();
            this.update_viewport_state();
            this.update_command_bar_height();

            const urlParams = new URLSearchParams(window.location.search);

            if (urlParams.has('show_sub_nav')) {
                this.show_sub_nav = urlParams.get('show_sub_nav') === 'true';
            } else {
                this.show_sub_nav = window.innerWidth >= 992;
            }

            if (window.innerWidth < 992) {
                this.show_info_nav = false;
            }

            window.addEventListener('resize', () => {
                this.update_viewport_state();
            });
        },

        start_resize_info(event) {
            if (!this.is_mobile) {
                this.is_resizing_info = true;
                this.resize_start_x = event.clientX;
                this.resize_start_width = this.info_nav_width;
            }
        },

        start_resize_sub(event) {
            if (!this.is_mobile) {
                let current_width = this.$refs.sub_nav_container.offsetWidth;
                this.sub_nav_width = current_width;
                this.sub_nav_has_been_resized = true;
                this.is_resizing_sub = true;
                this.resize_start_x = event.clientX;
                this.resize_start_width = current_width;
            }
        },

        on_window_mousemove(event) {
            if (this.is_resizing_sub && !this.is_mobile) {
                let delta = event.clientX - this.resize_start_x;
                this.sub_nav_width = this.resize_start_width + delta;

                if (this.sub_nav_width < this.sub_nav_min_width) this.sub_nav_width = this.sub_nav_min_width;
                if (this.sub_nav_width > this.sub_nav_max_width) this.sub_nav_width = this.sub_nav_max_width;
            }

            if (this.is_resizing_info && !this.is_mobile) {
                let delta = this.resize_start_x - event.clientX;
                this.info_nav_width = this.resize_start_width + delta;

                if (this.info_nav_width < this.info_nav_min_width) this.info_nav_width = this.info_nav_min_width;
                if (this.info_nav_width > this.info_nav_max_width) this.info_nav_width = this.info_nav_max_width;
            }
        },

        on_window_mouseup() {
            this.is_resizing_sub = false;
            this.is_resizing_info = false;
        },

        close_info() {
            this.show_info_nav = false;
        },

        close_sub() {
            this.show_sub_nav = false;
        },

        toggle_info() {
            this.show_info_nav = !this.show_info_nav;

            if (this.is_narrow_viewport) {
                this.show_sub_nav = false;
            }
        },

        toggle_sub() {
            this.show_sub_nav = !this.show_sub_nav;

            if (this.is_narrow_viewport) {
                this.show_info_nav = false;
            }
        }
    }));
});
