const KNOWLEDGE_ENTRY_VERSION_EDITOR = new EditorJS({
    holder: 'knowledge-entry-version-editor',
    readOnly: true,
    // TODO: Consider storing this data in db to make editor runtime configurable
    tools: {
        text: {
            class: Paragraph,
            inlineToolbar: true,
            placeholder: 'Write something awesome!',
        },
        heading: {
            class: Header,
            inlineToolbar: true,
            config: {
                placeholder: 'Enter heading text...',
                levels: [1, 2, 3, 4, 5, 6],
                defaultLevel: 1
            }
        },
        list: {
            class: EditorjsList,
            inlineToolbar: true,
            config: {
                defaultStyle: 'unordered'
            },
        }
    },
    defaultBlock: 'text'
});

document.addEventListener('DOMContentLoaded', () => {
    const initial_block_data_string = document.getElementById('initial-block-data')?.innerText

    if (initial_block_data_string) {
        try {
            const initial_block_data = JSON.parse(initial_block_data_string)
            if (initial_block_data) {
                KNOWLEDGE_ENTRY_VERSION_EDITOR.blocks.render(initial_block_data)
            }
        }
        catch (e) {
            console.error('Invalid JSON found in included initial block data')
        }
    }
})
