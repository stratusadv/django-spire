function create_editorjs_instance({holder_id, update_url, initial_editor_blocks}) {
    return new EditorJS({
        holder: holder_id,
        readOnly: !should_init_editor_in_edit_mode(),
        tools: {
            text: {
                class: Paragraph,
                inlineToolbar: true,
                config: {
                    placeholder: 'Write something awesome!',
                }
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
            },
            paragraph: NullParagraph
        },
        defaultBlock: 'text',
        onChange: async (api, _) => {
            const raw_editor_blocks = await api.saver.save()

            const parsed_editor_blocks = raw_editor_blocks.blocks.map((block, i) => ({
                id: block.id,
                order: i,
                data: block.data,
                type: block.type,
                tunes: block?.tunes ?? {},
            }))

           try {
                await django_glue_fetch(
                    update_url,
                    {
                        payload: parsed_editor_blocks,
                    }
                )
            }
            catch (e) {
                console.error('Error saving editor blocks', e)
                const event_detail = {
                    'id': Date.now(),
                    'type': 'error',
                    'message': 'Something went wrong when saving your changes. Please reload the page and try again.'
                }

                const editor_error_event = new CustomEvent('notify', { detail: event_detail })
                window.dispatchEvent(editor_error_event)
            }
        },
        onReady: () => {
            try {
                if (initial_editor_blocks.length > 0) {
                    KNOWLEDGE_ENTRY_VERSION_EDITOR.blocks.render({
                        blocks: initial_editor_blocks,
                    })
                    if (should_init_editor_in_edit_mode()) {
                        focus_editor()
                    }

                    const block_id = new URLSearchParams(window.location.search).get('block_id')

                    if (block_id) {
                        setTimeout(() => {
                            const element = document.querySelector(`[data-id="${block_id}"]`)
                            console.log('element', element)
                            if (element) {
                                element.scrollIntoView({behavior: 'smooth', block: 'center'})
                                element.style.transition = 'background-color 1s ease'
                                element.classList.add('bg-app-accent-soft', 'mx-3', 'rounded-3')
                                setTimeout(() => {
                                    element.classList.remove('bg-app-accent-soft')
                                }, 4000)
                            }
                        }, 100)
                    }

                }
            }
            catch (e) {
                console.error('Invalid JSON found in included initial block data', e)
            }
        }
    })
}

function focus_editor() {
    // editor seems to have trouble focusing without this slight setTimeout applied
    setTimeout(() => KNOWLEDGE_ENTRY_VERSION_EDITOR.focus(), 10)
}

function should_init_editor_in_edit_mode() {
    return new URLSearchParams(window.location.search).get('view_mode') === 'edit'
}
