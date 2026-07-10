window.Spire = window.Spire || {};

let lastTouchedElement = null;

document.addEventListener('touchstart', function (e) {
    lastTouchedElement = e.target;
}, {passive: true});

Spire.pullToRefresh = {
    /**
     * @param {Element} element
     * @returns {Element|null}
     */
    getScrollableAncestor(element) {
        while (element && element !== document.body) {
            const style = window.getComputedStyle(element);
            const overflowY = style.getPropertyValue('overflow-y');

            if (
                (overflowY === 'auto' || overflowY === 'scroll') &&
                element.scrollHeight > element.clientHeight
            ) {
                return element;
            }

            element = element.parentElement;
        }

        return null;
    },

    isIOS() {
        return /iPhone|iPad|iPod/i.test(navigator.userAgent);
    },

    isWebkit() {
        return /WebKit/i.test(navigator.userAgent) && !/Chrome/i.test(navigator.userAgent);
    },

    isStandaloneMode() {
        return window.navigator.standalone === true ||
            window.matchMedia('(display-mode: standalone)').matches;
    }
};

const ptr = PullToRefresh.init({
    mainElement: 'body',

    shouldPullToRefresh: function () {
        if (!(Spire.pullToRefresh.isIOS() && Spire.pullToRefresh.isWebkit() && Spire.pullToRefresh.isStandaloneMode())) {
            return false;
        }

        const scrollable = Spire.pullToRefresh.getScrollableAncestor(lastTouchedElement);

        if (scrollable) {
            return false;
        }

        return document.scrollingElement.scrollTop === 0;
    },

    onRefresh() {
        window.location.reload();
    }
});