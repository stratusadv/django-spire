document.addEventListener('alpine:init', () => {
    // Reads and writes the file through its glueField's value.
    Alpine.data('glueSingleFileField', () => ({
        preview: null,
        current_file: null,

        init() {
            if (this.value && typeof this.value === 'string') {
                try {
                    let file_data = JSON.parse(this.value);
                    if (file_data.preview) {
                        this.preview = file_data.preview;
                        this.current_file = file_data;
                    }
                } catch (e) {}
            }
        },

        handle_file_change(event) {
            const file = event.target.files[0];
            if (file) {
                this.value = file;
                if (file.type.startsWith('image/')) {
                    let reader = new FileReader();
                    reader.onload = (e) => { this.preview = e.target.result; };
                    reader.readAsDataURL(file);
                }
            }
        },

        clear_file() {
            this.value = null;
            this.preview = null;
            this.current_file = null;
        },
    }));
});
