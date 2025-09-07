document.querySelectorAll('template[x-component]').forEach(template => {

    const name = `x-${template.getAttribute('x-component')}`;

    class Component extends HTMLElement {
        connectedCallback() {
            if (!this._initialized) {
                this._initialized = true;
                const clone = template.content.cloneNode(true);
                const dataBinding = this.getAttribute(':data');
                if (dataBinding) {
                    const wrapper = document.createElement('div');
                    wrapper.setAttribute('x-data', `{ data: ${dataBinding} }`);
                    wrapper.appendChild(clone);
                    this.append(wrapper);
                } else {
                    this.append(clone);
                }
            }
        }
    }

    if (!customElements.get(name)) {
        customElements.define(name, Component);
    }
});
