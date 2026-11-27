import {describe, expect, test} from 'bun:test'

describe('Spire.date.addDays', () => {
    test.each([
        ['no days', '2026-11-24', 0, '2026-11-24'],
        ['days within a month', '2026-11-06', 15, '2026-11-21'],
        ['into the next month', '2026-11-24', 30, '2026-12-24'],
        ['into the next year', '2026-12-20', 15, '2027-01-04'],
        ['onto a leap day', '2028-02-28', 1, '2028-02-29'],
        ['past February in a common year', '2027-02-28', 1, '2027-03-01'],
        ['back a few days', '2026-03-02', -3, '2026-02-27'],
        ['across the spring daylight saving change', '2026-03-07', 2, '2026-03-09'],
    ])('moves a date by %s', (_case, isoDate, days, expected) => {
        expect(Spire.date.addDays(isoDate, days)).toBe(expected)
    })

    test('coerces numeric string days and returns empty string for empty or invalid input', () => {
        expect(Spire.date.addDays('2026-12-20', '15')).toBe('2027-01-04')
        expect(Spire.date.addDays('', 15)).toBe('')
        expect(Spire.date.addDays(null, 15)).toBe('')
        expect(Spire.date.addDays('2026-12-20', Number.NaN)).toBe('')
    })
})
