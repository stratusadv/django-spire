class Entry {
    constructor({
        entry_id,
        name,
        version_id,
        author,
        status,
        last_edit_datetime,
        publish_datetime,
        view_url,
        edit_url,
        edit_version_url,
        delete_url,
    }) {
        this.entry_id = entry_id
        this.name = name
        this.version_id = version_id
        this.author = author
        this.status = status
        this.last_edit_datetime = last_edit_datetime
        this.publish_datetime = publish_datetime
        this.view_url = view_url
        this.edit_url = edit_url
        this.delete_url = delete_url
        this.edit_version_url = edit_version_url
    }
}

class Collection {
    constructor({
        id = -1,
        name = 'None',
        description = '',
        order = 0,
        parent = null,
        children = [],
        entries = [],
        delete_url = '',
        edit_url = '',
        create_entry_url = '',
        import_entry_url = '',
    }) {
        this.id = id
        this.name = name
        this.description = description
        this.order = order
        this.parent = parent
        this.children = children
        this.entries = entries
        this.delete_url = delete_url
        this.edit_url = edit_url
        this.create_entry_url = create_entry_url
        this.import_entry_url = import_entry_url
        this.show_details = false
    }

    has_child_collections() {
        return this.children.length > 0
    }

    has_entries() {
        return this.entries.length > 0
    }

    toggle_show_details({value = false}) {
        this.show_details = value

        this.children.forEach(child => {
            child.toggle_show_details({value: false})
        });
    }
}

class CollectionManager {
    constructor(collection_tree){
        this.collection_lookup_map = new Map()
        this.collection_map = this._create_tree_structure({collections: collection_tree})
    }

    _create_entries({entries_json}) {
        let entries = []

        entries_json.forEach(entry => {
            entries.push(new Entry({
                entry_id: entry.entry_id,
                name: entry.name,
                version_id: entry.version_id,
                author: entry.author,
                status: entry.status,
                last_edit_datetime: entry.last_edit_datetime,
                publish_datetime: entry.publish_datetime,
                view_url: entry.view_url,
                edit_url: entry.edit_url,
                edit_version_url: entry.edit_version_url,
                delete_url: entry.delete_url,
            }))
        })

        return entries
    }

    _create_tree_structure({collections}) {
        return collections.map((collection, index) => {
            const collection_object = new Collection({
                id: collection.id,
                name: collection.name,
                description: collection.description,
                order: collection.order,
                parent: new Collection({}),
                children: this._create_tree_structure({collections: collection.children}),
                entries: this._create_entries({entries_json: collection.entries}),
                delete_url: collection.delete_url,
                edit_url: collection.edit_url,
                create_entry_url: collection.create_entry_url,
                import_entry_url: collection.import_entry_url
            })

            this.collection_lookup_map.set(collection_object.id, collection_object)

            collection_object.children.forEach(child => {
                child.parent = collection_object;
            });

            return collection_object
        })
    }

    _show_details_to_root({collection}) {
        collection.show_details = true

        if (collection.parent) {
            this._show_details_to_root({collection: collection.parent})
        }
    }

    open_path_to({collection_id}) {
        const target_collection = this.collection_lookup_map.get(collection_id)

        this._show_details_to_root({collection: target_collection})
    }

    set_parent({collection, parent_id}) {
        collection.parent = this.collection_lookup_map.get(parent_id)
        if (collection.parent) {
            this.open_path_to({collection_id: collection.parent.id})
        }
    }
}
