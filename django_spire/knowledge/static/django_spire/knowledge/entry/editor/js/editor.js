class Block {
    constructor({value, type, update_template_rendered}) {
        this.value = value
        this.type = type
        this.update_template_rendered = update_template_rendered
    }
}

class EntryVersionBlock {
    constructor({id, type, order, block}) {
        this.id = id
        this.type = type
        this.order = order
        this.block = new Block({
            value: block.value,
            type: block.type,
            update_template_rendered: block.update_template_rendered
        })
    }
}

class EntryVersion {
    constructor({id, version_blocks_json}) {
        this.id = id
        this.version_blocks = []

        version_blocks_json.forEach(
            version_block => {
                this.version_blocks.push(
                    new EntryVersionBlock({
                        id: version_block.id,
                        type: version_block.type,
                        order: version_block.order,
                        block: version_block.block,
                    })
                )
            }
        )
    }
}

class Editor {
    constructor({id, version_blocks_json}) {
        this.entry_version = new EntryVersion({
            id: id,
            version_blocks_json: version_blocks_json
        })
        this.block_order_focus = 1
    }

    get_block_length({order}) {
        const version_block = this.entry_version.version_blocks.find(
            version_block => version_block.order === order
        )
        version_block.block.value = version_block.block.value + ' '
        return version_block.block.value.length
    }

    delete_block({id}) {
        const version_block = this.entry_version.version_blocks.find(
            version_block => version_block.id === id
        )
        if (version_block.order > 0) {
            this.block_order_focus = version_block.order - 1
        }

        this.entry_version.version_blocks = this.entry_version.version_blocks.filter(
            version_block => version_block.id !== id
        )
    }

    insert_blank_block({id, block_type, order, update_template_rendered}) {
        this.entry_version.version_blocks.forEach(
            version_block => {
                if (version_block.order >= order) {
                    version_block.order += 1
                }
            }
        )

        this.entry_version.version_blocks.push(
            new EntryVersionBlock({
                id: id,
                type: block_type,
                order: order,
                block: new Block({
                    value: '',
                    type: block_type,
                    update_template_rendered: update_template_rendered
                })
            })
        )

        this.entry_version.version_blocks.sort(
            (a, b) => a.order - b.order
        )

        this.block_order_focus = order
    }

    update_block_order_focus({order}) {
        this.block_order_focus = order
    }
}
