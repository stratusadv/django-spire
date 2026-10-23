document.addEventListener('alpine:init', () => {
    Alpine.data('messageNotifications', (initialNotifications) => ({
        notifications: initialNotifications,

        add(e) {
            this.notifications.push({
                'id': e.timeStamp,
                'type': e.detail.type,
                'message': e.detail.message
            });
        },

        remove(notification) {
            this.notifications = this.notifications.filter(i => i.id !== notification.id);
        }
    }));
});

document.addEventListener('alpine:init', () => {
    Alpine.data('messageToast', (notification, removeNotification) => ({
        show: false,

        init() {
            this.$nextTick(() => this.show = true);
            setTimeout(() => this.transitionOut(), 5000);
        },

        transitionOut() {
            this.show = false;
            setTimeout(() => removeNotification(notification), 500);
        }
    }));
});
