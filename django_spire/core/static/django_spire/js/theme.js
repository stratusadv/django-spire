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