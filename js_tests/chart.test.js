import {afterEach, beforeEach, describe, expect, spyOn, test} from 'bun:test'

let appended

beforeEach(() => {
    appended = []
    // A test never fetches echarts: the script is kept, not inserted.
    spyOn(document.head, 'appendChild').mockImplementation((element) => {
        appended.push(element)
        return element
    })
})

afterEach(() => {
    document.head.appendChild.mockRestore()
    Spire.chart._echarts = null
    delete window.echarts
})

function finishLoading(echarts) {
    window.echarts = echarts
    appended[0].onload()
}

describe('Spire.chart.loadEcharts', () => {
    test('adds one script for every chart that asks', async () => {
        const first = Spire.chart.loadEcharts()
        const second = Spire.chart.loadEcharts()

        expect(first).toBe(second)
        expect(appended.length).toBe(1)
        expect(appended[0].src).toBe(Spire.chart.ECHARTS_URL)
        expect(appended[0].integrity).toBe(Spire.chart.ECHARTS_INTEGRITY)

        const echarts = {init() {}}
        finishLoading(echarts)

        expect(await first).toBe(echarts)
    })

    test('keeps a copy of echarts the page loaded itself', async () => {
        const echarts = {init() {}}
        window.echarts = echarts

        expect(await Spire.chart.loadEcharts()).toBe(echarts)
        expect(appended.length).toBe(0)
    })

    test('tries again after a failed load', async () => {
        const failed = Spire.chart.loadEcharts()
        appended[0].onerror()

        await expect(failed).rejects.toThrow('echarts did not load')

        Spire.chart.loadEcharts()

        expect(appended.length).toBe(2)
    })

    test('lets signage theme a chart before the chart starts', async () => {
        await import('../django_spire/metric/visual/signage/static/django_spire/metric/visual/signage/js/kiosk_chart.js')

        const themes = []
        const chart = (async () => {
            const echarts = await Spire.chart.loadEcharts()
            echarts.init(document.createElement('div'))
        })()

        finishLoading({
            init(element, theme) {
                themes.push(theme)
                return {setOption() {}, resize() {}, getHeight: () => 0}
            },
        })
        await chart

        expect(window.echarts._kioskThemePatched).toBe(true)
        expect(themes.length).toBe(1)
        expect(themes[0].textStyle.fontSize).toBeDefined()
    })

    test('runs a patch registered first before a chart that awaits it', async () => {
        const order = []
        Spire.chart.loadEcharts().then(() => order.push('patch'))
        const chart = (async () => {
            await Spire.chart.loadEcharts()
            order.push('chart')
        })()

        finishLoading({init() {}})
        await chart

        expect(order).toEqual(['patch', 'chart'])
    })
})
