function get_cookie(name) {
    let cookieValue = null

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }

    return cookieValue
}


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

export {
    ajax_request,
    get_cookie,
}