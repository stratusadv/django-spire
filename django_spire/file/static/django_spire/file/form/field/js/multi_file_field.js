document.addEventListener('alpine:init', () => {
    // Reads and writes the files through its glueField's value.
    Alpine.data('glueMultiFileField', ({ max_files, accept, maximum_filesize }) => ({
        show_dropdown: false,
        files: [],
        objects: {},
        is_multiple: true,
        max_files,

        accept,
        maximum_filesize: maximum_filesize * 1024 * 1024,
        units: ['B', 'KB', 'MB', 'GB'],

        init() {
            if (!this.value) return;
            try {
                this.files = Array.isArray(this.value) ? this.value : JSON.parse(this.value);
            } catch (e) {
                this.files = [];
            }
        },

        format_file_size(bytes) {
            if (!bytes) return '';
            let size = bytes;
            let index = 0;
            while (size >= 1024 && index < this.units.length - 1) {
                size /= 1024;
                index++;
            }
            return size.toFixed(1) + ' ' + this.units[index];
        },

        truncate_name(name, max = 30) {
            return name && name.length > max ? name.slice(0, max - 3) + '...' : name;
        },

        handle_files_change(event) {
            const new_files = Array.from(event.target.files || []);
            if (this.max_files && (this.files.length + new_files.length) > this.max_files) {
                return;
            }
            for (let file of new_files) {
                if (file.size > this.maximum_filesize) continue;
                let file_id = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                this.files.push({ id: file_id, name: file.name, size: file.size, file: file });
                this.objects[file_id] = file;
                if (file.type.startsWith('image/')) {
                    // The list's own entry is reactive, so the preview shows once it loads.
                    let entry = this.files[this.files.length - 1];
                    let reader = new FileReader();
                    reader.onload = (e) => { entry.preview = e.target.result; };
                    reader.readAsDataURL(file);
                }
            }
            this.update_value();
            event.target.value = '';
        },

        remove_file(file_id) {
            this.files = this.files.filter(f => f.id !== file_id);
            delete this.objects[file_id];
            this.update_value();
        },

        update_value() {
            const uploaded = this.files.map(f => f.file).filter(f => f);
            this.value = uploaded.length ? uploaded : null;
        },
    }));
});
