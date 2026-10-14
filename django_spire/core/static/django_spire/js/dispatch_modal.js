document.addEventListener('alpine:init', () => {
    Alpine.data('dispatchModal', () => ({
        eventData: {},
        modal: null,
        dialogClasses: '',
        removeContentScope: null,

        init() {
            this.modal = bootstrap.Modal.getOrCreateInstance(this.$el);
            this.$el.addEventListener('show.bs.modal', () => this.$el.removeAttribute('inert'));
            this.$el.addEventListener('hide.bs.modal', () => this.$el.setAttribute('inert', ''));
        },

        setUp(event) {
            this.dialogClasses = event.detail.dialogClasses || '';
            this.eventData = event.detail.eventData;
            const contentElement = document.getElementById(
                event.detail.renderToBody ? 'baseDispatchModalBody' : 'baseDispatchModalContent'
            );

            this.removeContentScope?.();
            contentElement.innerHTML = event.detail.htmlContent;

            window.Glue?.registerComponentsFromDom(contentElement);

            if (event.detail.scopeData) {
                this.removeContentScope = Alpine.addScopeToNode(
                    contentElement,
                    event.detail.scopeData
                );
            } else {
                this.removeContentScope = null;
            }

            this.showModal();
        },

        hideModal() {
            this.modal.hide();
        },

        showModal() {
            this.modal.show();
        }
    }));
});
