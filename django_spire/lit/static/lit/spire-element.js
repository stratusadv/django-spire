import { LitElement } from 'https://cdn.jsdelivr.net/npm/lit@3/+esm';

/**
 * Base class for Spire Lit components.
 *
 * Extends LitElement with:
 * - Light DOM rendering (no Shadow DOM) to inherit global styles like Bootstrap
 * - Access to Spire and Glue globals
 *
 * Usage:
 *   import SpireElement from '/static/lit/spire-element.js';
 *   import { html } from 'https://cdn.jsdelivr.net/npm/lit@3/+esm';
 *
 *   export default class MyComponent extends SpireElement {
 *       render() {
 *           return html`<div class="btn btn-primary">Hello</div>`;
 *       }
 *   }
 */
export default class SpireElement extends LitElement {
    /**
     * Use light DOM instead of Shadow DOM.
     * This allows global styles (Bootstrap, etc.) to affect component content.
     */
    createRenderRoot() {
        return this;
    }

    /**
     * Access the Glue global.
     */
    get Glue() {
        return window.Glue;
    }

    /**
     * Access the Spire global.
     */
    get Spire() {
        return window.Spire;
    }
}

// Re-export html and css from Lit for convenience
export { html, css } from 'https://cdn.jsdelivr.net/npm/lit@3/+esm';
