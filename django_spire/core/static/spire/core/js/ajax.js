async function ajax_request(method, url, data) {
    return axios({
        method: method,
        url: url,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': get_cookie('csrftoken'),
        },
        data: {
            'data': data,
        }
    })
}

function dispatchActiveShelterUpdate(shelter_id){
    window.dispatchEvent(new CustomEvent('active-shelter-update', {detail:{shelter_id: shelter_id}}))
}

function dispatchRemainingShelterUpdate(field_id){
    window.dispatchEvent(new CustomEvent('remaining-shelter-update', {detail:{field_id: field_id}}))
}

function dispatchCurrentPositionClicked(field_id){
    window.dispatchEvent(new CustomEvent('current-position-clicked', {detail:{field_id: field_id}}))
}
