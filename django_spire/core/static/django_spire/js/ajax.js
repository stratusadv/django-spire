async function ajax_request(method, url, data) {
    return axios({
        method: method,
        url: url,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': get_cookie('csrftoken'),
        },
        data: data
    })
}