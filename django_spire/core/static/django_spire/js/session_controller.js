class SessionController {
    constructor(session_json) {
        this.data = JSON.parse(session_json);
    }

    get_data(key, default_value) {
        return this.data[key] !== undefined ? this.data[key] : default_value;
    }

}