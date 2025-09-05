class Collection {
    constructor({id, name, description, order, children = []}) {
        this.id = id
        this.name = name
        this.description = description
        this.order = order
        this.children = children
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
                children: this.create_tree_structure({collections: collection.children})
            })

            this.collection_lookup_map.set(collection_object.id, collection_object)

            return collection_object
        })
    }
}