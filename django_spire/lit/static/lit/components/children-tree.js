import SpireElement, { html } from '/static/lit/spire-element.js';

/**
 * Recursive children tree component.
 * Wraps an item template and handles recursive child loading/rendering.
 *
 * Usage:
 *   <children-tree
 *       x-prop:item="item"
 *       x-prop:getChildren="async (item) => {
 *           const result = await item.children.filter({is_active: true}).all();
 *           return result.items;
 *       }"
 *   >
 *       <!-- Your item template - rendered once for this item, cloned for children -->
 *       <div class="item-row">
 *           <span x-text="item.name"></span>
 *       </div>
 *   </children-tree>
 */
export default class ChildrenTree extends SpireElement {
    static properties = {
        item: { type: Object },
        getChildren: { type: Function },
        showChildren: { type: Boolean, state: true },
        childrenLoaded: { type: Boolean, state: true },
        children: { type: Array, state: true },
    };

    constructor() {
        super();
        this.item = null;
        this.getChildren = null;
        this.showChildren = false;
        this.childrenLoaded = false;
        this.children = [];
        this._template = null;
    }

    connectedCallback() {
        super.connectedCallback();
        // Capture the slot content as a template before we modify anything
        if (!this._template) {
            this._template = this.innerHTML;
        }

        // Listen for toggle event from slot content
        this.addEventListener('toggle-children', (e) => {
            e.stopPropagation();
            this.toggleChildren();
        });
    }

    get hasChildren() {
        return !!this.getChildren;
    }

    async toggleChildren() {
        if (!this.showChildren && !this.childrenLoaded && this.getChildren) {
            this.children = await this.getChildren(this.item) || [];
            this.childrenLoaded = true;
            this._renderChildren();
        }
        this.showChildren = !this.showChildren;

        // Toggle class for CSS-based chevron rotation
        this.classList.toggle('expanded', this.showChildren);

        // Dispatch event for Alpine to update chevron
        this.dispatchEvent(new CustomEvent('children-expanded', {
            detail: { expanded: this.showChildren },
            bubbles: true
        }));
    }

    _renderChildren() {
        if (!this._template || this.children.length === 0) {
            return;
        }

        const container = this.renderRoot.querySelector('.children-container');
        if (!container) {
            return;
        }

        container.innerHTML = '';

        this.children.forEach(child => {
            // Create a new children-tree for each child
            const childTree = document.createElement('children-tree');
            childTree.item = child;
            childTree.getChildren = this.getChildren;
            childTree._template = this._template;
            childTree.innerHTML = this._template;

            container.appendChild(childTree);

            // Initialize Alpine on the cloned content
            requestAnimationFrame(() => {
                if (window.Alpine) {
                    // Create Alpine scope with the child item
                    childTree._x_dataStack = [{ item: child }];
                    Alpine.initTree(childTree);
                }
            });
        });
    }

    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has('showChildren') && this.showChildren && this.childrenLoaded) {
            this._renderChildren();
        }
    }

    render() {
        // No wrapper divs - just slot and children container
        // The chevron toggle is exposed via toggleChildren method for the template to call
        return html`
            <slot></slot>
            ${this.hasChildren ? html`
                <div class="children-container ms-4"
                     style="display: ${this.showChildren ? 'block' : 'none'}">
                </div>
            ` : ''}
        `;
    }
}
