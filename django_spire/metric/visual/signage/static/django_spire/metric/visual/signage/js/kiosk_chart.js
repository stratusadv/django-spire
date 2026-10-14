(function () {
    const root = document.documentElement;
    const zoom = parseFloat(getComputedStyle(root).getPropertyValue('--signage-zoom')) || 1;
    if (window.innerHeight / zoom < 240) {
        root.style.setProperty('--signage-zoom', '1');
    }

    const truncate = (name) => (name.length > 28 ? '…' + name.slice(-27) : name);
    const GAUGE_FONT_BASE = 21.6;
    const GAUGE_ZOOM_CAP = 1.25;
    const attach = () => {
        if (!window.echarts || echarts._kioskThemePatched) return;
        echarts._kioskThemePatched = true;
        const fontSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
        const theme = {
            textStyle: { fontSize: fontSize },
            legend: { textStyle: { fontSize: fontSize } },
            xAxis: { axisLabel: { fontSize: fontSize } },
            yAxis: { axisLabel: { fontSize: fontSize } },
            tooltip: { textStyle: { fontSize: fontSize } },
        };
        const originalInit = echarts.init;
        echarts.init = (el, themeOverride, opts) => {
            const chart = originalInit(el, themeOverride || theme, opts);
            const originalSetOption = chart.setOption.bind(chart);
            chart.setOption = (option, setOpts) => {
                chart._kioskLastOption = option;
                const fontSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
                option = { ...(option || {}) };

                option.textStyle = { ...(option.textStyle || {}), fontSize: fontSize };

                if (option.legend) {
                    option.legend = {
                        ...option.legend,
                        bottom: 8,
                        formatter: truncate,
                        textStyle: { ...(option.legend.textStyle || {}), fontSize: fontSize },
                    };
                }
                for (const axis of [option.xAxis, option.yAxis]) {
                    if (Array.isArray(axis)) {
                        axis.forEach((a) => (a.axisLabel = { ...(a.axisLabel || {}), fontSize: fontSize }));
                    } else if (axis) {
                        axis.axisLabel = { ...(axis.axisLabel || {}), fontSize: fontSize };
                    }
                }
                if (option.xAxis || option.yAxis) {
                    option.grid = {
                        ...(option.grid || {}),
                        left: fontSize * 2 + 10,
                        right: fontSize,
                        top: fontSize,
                        bottom: fontSize * 3 + 16,
                    };
                }
                const boxW = chart.getWidth();
                const boxH = chart.getHeight();
                for (const series of option.series || []) {
                    if (series.type === 'pie') {
                        const label = {
                            ...(series.label || {}),
                            show: true,
                            formatter: (params) => truncate(params.name),
                        };
                        if (boxW > 0 && boxH > 0) {
                            label.overflow = 'truncate';
                            label.width = Math.floor(boxW * 0.35);
                        }
                        series.label = label;
                        if (boxW > 0 && boxH > 0) {
                            const data = series.data || [];
                            const legendWidth = boxW * 0.9;
                            const legendItemsWidth =
                                data.reduce(
                                    (sum, d) => sum + 30 + Math.min(String(d.name || '').length, 28) * fontSize * 0.5,
                                    0,
                                ) + (data.length - 1) * 5;
                            const legendRows = Math.max(1, Math.ceil(legendItemsWidth / legendWidth));
                            const legendTop = boxH - 8 - legendRows * (Math.max(fontSize, 14) + 9);

                            let outer = series.radius;
                            if (Array.isArray(outer)) {
                                outer = outer[outer.length - 1];
                            }
                            const minSide = Math.min(boxW, boxH);
                            const radius =
                                typeof outer === 'number'
                                    ? outer
                                    : ((parseFloat(outer) || 50) / 100) * (minSide / 2);
                            const center = series.center;
                            const centerX =
                                Array.isArray(center) && center[0]
                                    ? (parseFloat(center[0]) / 100) * boxW
                                    : 0.5 * boxW;
                            const centerY =
                                Array.isArray(center) && center[1]
                                    ? (parseFloat(center[1]) / 100) * boxH
                                    : 0.45 * boxH;

                            const shiftPlan = {};
                            if (radius > 0) {
                                const total = data.reduce((sum, d) => sum + (d.value || 0), 0);

                                if (total > 0) {
                                    const shifted = [];
                                    let cumulative = 0;

                                    data.forEach((d, i) => {
                                        const start = cumulative / total;
                                        cumulative += d.value || 0;
                                        const midAngle = ((start + cumulative / total) / 2) * 2 * Math.PI;
                                        const labelBottom = centerY - (radius + 15) * Math.cos(midAngle) + fontSize / 2;

                                        if (labelBottom > legendTop + fontSize * 0.5) {
                                            shifted.push(i);
                                        }
                                    });

                                    shifted.forEach((index, k) => {
                                        shiftPlan[index] = {
                                            x: Math.round(centerX - radius - Math.max(radius * 0.25, fontSize * 0.5)),
                                            y: Math.round(
                                                centerY - ((shifted.length - 1) * (fontSize + 6)) / 2 + k * (fontSize + 6),
                                            ),
                                        };
                                    });
                                }
                            }

                            series.labelLayout = (params) => {
                                const plan = shiftPlan[params.dataIndex];
                                if (plan) {
                                    const labelW = params.labelRect ? Math.round(params.labelRect.width) : 0;

                                    return { ...plan, x: Math.max(plan.x, labelW + 2), align: 'right', hideOverlap: true };
                                }
                                const rect = params.labelRect;

                                if (rect && rect.y + rect.height > legendTop) {
                                    return { y: Math.round(legendTop - rect.height), hideOverlap: true };
                                }

                                return { hideOverlap: true };
                            };
                        } else {
                            series.labelLayout = { ...(series.labelLayout || {}), hideOverlap: true };
                        }
                    }
                    if (series.type === 'gauge') {
                        const zoom = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--signage-zoom')) || 1;
                        const scale = Math.round((fontSize / GAUGE_FONT_BASE) * (Math.min(zoom, GAUGE_ZOOM_CAP) / zoom) * 100) / 100;
                        series.axisLine = {
                            ...(series.axisLine || {}),
                            lineStyle: {
                                ...(series.axisLine?.lineStyle || {}),
                                width: Math.round(10 * scale),
                            },
                        };
                        series.splitLine = {
                            ...(series.splitLine || {}),
                            length: Math.round(10 * scale),
                            distance: Math.round(10 * scale),
                        };
                        series.axisTick = {
                            ...(series.axisTick || {}),
                            length: Math.round(6 * scale),
                            distance: Math.round(10 * scale),
                        };
                        series.axisLabel = {
                            ...(series.axisLabel || {}),
                            distance: Math.round(15 * scale),
                            fontSize: Math.round(12 * scale),
                        };
                        series.pointer = {
                            ...(series.pointer || {}),
                            width: Math.round(6 * scale),
                        };
                        const titleFont = Math.round(16 * scale);
                        series.title = {
                            ...(series.title || {}),
                            fontSize: titleFont,
                        };
                        series.detail = {
                            ...(series.detail || {}),
                            width: Math.round(100 * scale),
                            fontSize: Math.round(30 * scale),
                        };

                        if (option.legend && boxW > 0 && boxH > 0) {
                            const radius = 0.375 * Math.min(boxW, boxH);
                            const titleBottom = boxH / 2 + radius * 0.7 + titleFont / 2;
                            const legendTop = boxH - 8 - fontSize - 6;

                            if (titleBottom > legendTop - 2) {
                                series.title = { ...series.title, show: false };
                            }
                        }
                    }
                }

                return originalSetOption(option, setOpts);
            };
            const originalResize = chart.resize.bind(chart);
            chart.resize = (w, h) => {
                const wasCollapsed = chart.getHeight() === 0;
                originalResize(w, h);
                if (wasCollapsed && chart.getHeight() > 0 && chart._kioskLastOption) {
                    chart.setOption(chart._kioskLastOption);
                }
            };
            return chart;
        };
    };
    const echartsTag = document.querySelector('script[src*="echarts"]');
    if (window.echarts) {
        attach();
    } else if (echartsTag) {
        echartsTag.addEventListener('load', attach);
    }
})();
