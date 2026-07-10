Spire.session = {
    Controller: class SessionController {
        constructor(session_json) {
            this.data = JSON.parse(session_json);
        }

        getData(key, default_value) {
            return this.data[key] !== undefined ? this.data[key] : default_value;
        }
    }
};