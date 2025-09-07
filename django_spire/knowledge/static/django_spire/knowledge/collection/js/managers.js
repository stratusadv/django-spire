class Collection {
    constructor({id = -1, name = 'None', description = '', order = 0, parent = null, children = []}) {
        this.id = id
        this.name = name
        this.description = description
        this.order = order
        this.children = children
        this.parent = parent
        this.show_children = false
    }

    has_children() {
        return this.children.length > 0
    }

    toggle_show_children({value = false}) {
        this.show_children = value

        this.children.forEach(child => {
            child.toggle_show_children({value: false})
        });
    }
}

class CollectionManager {
    constructor(collection_tree){
        this.collection_lookup_map = new Map()
        this.collection_map = this.create_tree_structure({collections: collection_tree})
    }

    create_tree_structure({collections}) {
        return collections.map((collection, index) => {
            const collection_object = new Collection({
                id: collection.id,
                name: collection.name,
                description: collection.description,
                order: collection.order,
                parent: new Collection({}),
                children: this.create_tree_structure({collections: collection.children})
            })

            this.collection_lookup_map.set(collection_object.id, collection_object)

            collection_object.children.forEach(child => {
                child.parent = collection_object;
            });

            return collection_object
        })
    }
}