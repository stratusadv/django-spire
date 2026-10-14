document.addEventListener('alpine:init', () => {
    Alpine.data('spireChart', () => ({
        chart: null,
        theme: {},
        _params: null,
        _update_timer: null,
        _resize_observer: null,

        get _glue_name() {
            return this.$el.dataset.chartGlueName || '';
        },

        get _update_interval() {
            return parseFloat(this.$el.dataset.chartUpdateInterval) || 3;
        },

        _gauge_detail_formatter(value_type) {
            const fixed = (number) =>
                number.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

            return (value) => {
                const number = Number(value ?? 0);

                if (value_type === 'percentage') {
                    return `${fixed(number)}%`;
                }
                if (value_type === 'currency') {
                    return `${number < 0 ? '-' : ''}$${fixed(Math.abs(number))}`;
                }
                return number.toLocaleString('en-US', {maximumFractionDigits: 2});
            };
        },

        _inject_gauge_formatters(option) {
            for (const series of option.series || []) {
                if (series.type !== 'gauge') continue;

                series.detail = {
                    ...(series.detail || {}),
                    formatter: this._gauge_detail_formatter(series.valueType),
                };
            }

            return option;
        },

        init() {
            this.theme = window.get_echarts_theme ? window.get_echarts_theme() : {};
            const option = this._themed(
                this._inject_gauge_formatters(JSON.parse(this.$el.querySelector('#chart-option').textContent))
            );
            this._params = JSON.parse(this.$el.querySelector('#chart-params').textContent);

            this.chart = echarts.init(this.$el);
            this.chart.setOption(option);

            this._resize_observer = new ResizeObserver(() => {
                if (this.chart) {
                    this.chart.resize();
                }
            });
            this._resize_observer.observe(this.$el);

            window.addEventListener('resize', () => this.chart && this.chart.resize());

            if (this._glue_name) {
                this._schedule_update();
            }
        },

        _themed(option) {
            option = { ...(option || {}) };
            const theme = this.theme;

            option.textStyle = { color: theme.text };
            option.color = option.color || [theme.primary, theme.success, theme.warning, theme.danger];
            option.tooltip = option.tooltip || {};
            option.tooltip.backgroundColor = theme.layer_two;
            option.tooltip.textStyle = option.tooltip.textStyle || {};
            option.tooltip.textStyle.color = theme.text;
            option.tooltip.borderColor = theme.border;

            return option;
        },

        async _update() {
            const proxy = window.Glue?.function?.[this._glue_name];

            if (!proxy) return;

            try {
                const response = await proxy.execute({'kwargs': this._params || {}});
                const option = response?.result?.result ?? response?.result ?? response;

                if (option) {
                    this.chart.setOption(this._themed(this._inject_gauge_formatters(option)), { notMerge: true });
                }
            } catch (error) {
                console.error('Chart update failed:', error);
            }
        },

        _schedule_update() {
            const schedule = () => {
                this._update_timer = setTimeout(async () => {
                    await this._update();
                    schedule();
                }, (this._update_interval + Math.random() * 2) * 1000);
            };

            schedule();
        },

        destroy() {
            if (this._update_timer) {
                clearTimeout(this._update_timer);
            }
            if (this._resize_observer) {
                this._resize_observer.disconnect();
            }
        }
    }));
});
