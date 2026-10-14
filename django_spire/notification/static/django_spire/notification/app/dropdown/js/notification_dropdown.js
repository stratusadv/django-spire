document.addEventListener('alpine:init', () => {
    Alpine.data('notificationDropdown', (checkUrl, dropdownUrl, setViewedUrl, listUrl) => ({
        hasContent: false,
        hasNewNotification: false,
        isLoading: false,

        async init() {
            await this.checkForNewNotifications();
            setInterval(() => this.checkForNewNotifications(), 30000);
        },

        async checkForNewNotifications() {
            let response = await Glue.fetch(checkUrl);
            this.hasNewNotification = response.has_new_notifications;
        },

        async renderDropdown() {
            if (this.isLoading) {
                return;
            }

            this.isLoading = true;

            try {
                let dropdownContent = Glue.view(
                    dropdownUrl,
                    {app_notification_list_url: listUrl}
                );

                await dropdownContent.renderInnerHtml(this.$refs.appNotificationDropdownContent);
                await this.markNotificationsAsViewed();
                this.hasContent = true;
            }
            finally {
                this.isLoading = false;
            }
        },

        async markNotificationsAsViewed() {
            await Glue.fetch(setViewedUrl);
            this.hasNewNotification = false;
        }
    }));
});
