Spire.date = {
    /**
     * @param {Date} date
     * @returns {string} Format: 'YYYY-MM-DDTHH:MM'
     */
    formatDatetimeInput(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    },

    /**
     * @param {Date} date
     * @returns {string} Format: 'YYYY-MM-DD'
     */
    formatDateInput(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    /**
     * A date input's value moved by a number of days, across months and years: addDays('2026-12-20', 15)
     * is '2027-01-04'. Counted in UTC, so a daylight saving change never shifts the day.
     *
     * @param {string} isoDate Format: 'YYYY-MM-DD'
     * @param {number} days May be negative.
     * @returns {string} Format: 'YYYY-MM-DD'
     */
    addDays(isoDate, days) {
        const [year, month, day] = isoDate.split('-').map(Number);
        return new Date(Date.UTC(year, month - 1, day + days)).toISOString().slice(0, 10);
    }
};