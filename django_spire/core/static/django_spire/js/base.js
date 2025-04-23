function div_to_form_data(div) {
    let inputs = div.querySelectorAll('input, textarea, select');

    let formData = new FormData();

    inputs.forEach(input => {
        if (input.name) {
            formData.append(input.name, input.value);
        }
    });

    return formData
}


function dispatch_modal(html_content) {
    window.dispatchEvent(
        new CustomEvent(
            'dispatch-modal',
            { detail: {'html_content': html_content}, bubbles: true }
        )
    )
}


function toggle_loading_overlay() {
    let body = document.body;
    let spinner = document.getElementById('loading-icon');

    if (body.classList.contains('darken-background')) {
        body.classList.remove('darken-background');
        spinner.classList.add('d-none');
    } else {
        body.classList.add('darken-background');
        spinner.classList.remove('d-none');
    }
}


function dispatch_success_notification(message){
    window.dispatchEvent(
        new CustomEvent(
            'notify',
            { detail: {'type': 'success', 'message': message}, bubbles: true }
        )
    )
}


function dispatch_error_notification(message){
    window.dispatchEvent(
        new CustomEvent(
            'notify',
            { detail: {'type': 'error', 'message': message}, bubbles: true }
        )
    )
}


var UUID = (function() {
    var self = {};
    var lut = [];

    for (var i = 0; i < 256; i++) {
        lut[i] = (i < 16 ? '0' : '') + (i).toString(16);
    }

    self.generate = function() {
        var d0 = Math.random() * 0xffffffff | 0;
        var d1 = Math.random() * 0xffffffff | 0;
        var d2 = Math.random() * 0xffffffff | 0;
        var d3 = Math.random() * 0xffffffff | 0;

        return lut[d0 & 0xff] + lut[d0 >> 8 & 0xff] + lut[d0 >> 16 & 0xff] + lut[d0 >> 24 & 0xff] + '-' +
            lut[d1 & 0xff] + lut[d1 >> 8 & 0xff] + '-' + lut[d1 >> 16 & 0x0f | 0x40] + lut[d1 >> 24 & 0xff] + '-' +
            lut[d2 & 0x3f | 0x80] + lut[d2 >> 8 & 0xff] + '-' + lut[d2 >> 16 & 0xff] + lut[d2 >> 24 & 0xff] +
            lut[d3 & 0xff] + lut[d3 >> 8 & 0xff] + lut[d3 >> 16 & 0xff] + lut[d3 >> 24 & 0xff];
    }

    return self;
})();


function generate_id() {
    return UUID.generate();
}
