document.addEventListener("DOMContentLoaded", function () {
    const notificationBell = document.getElementById("notification-bell");
    const notificationDropdown = document.getElementById("notification-dropdown");
    const notificationList = document.getElementById("notification-list");
    const notificationCount = document.getElementById("notification-count");
    const noNotificationsMessage = document.getElementById("no-notifications");

    // Переключение видимости уведомлений
    notificationBell.addEventListener("click", function (event) {
        event.stopPropagation();
        notificationDropdown.classList.toggle("show");
    });

    // Закрытие уведомлений при клике вне окна
    document.addEventListener("click", function (event) {
        if (!notificationBell.contains(event.target) && !notificationDropdown.contains(event.target)) {
            notificationDropdown.classList.remove("show");
        }
    });

    // Функция загрузки уведомлений
    async function fetchNotifications() {
        try {
            const response = await fetch("/notifications");
            if (!response.ok) {
                console.error("Ошибка сервера:", response.status);
                return;
            }

            const notifications = await response.json();
            notificationList.innerHTML = "";

            if (notifications.length === 0) {
                noNotificationsMessage.style.display = "block";
                notificationCount.textContent = "0";
                notificationCount.style.display = "none";
            } else {
                noNotificationsMessage.style.display = "none";
                notificationCount.textContent = notifications.length;
                notificationCount.style.display = "inline-block";

                notifications.forEach(notification => {
                    const listItem = document.createElement("li");
                    listItem.textContent = notification.message;
                    notificationList.appendChild(listItem);
                });
            }
        } catch (error) {
            console.error("Ошибка загрузки уведомлений:", error);
        }
    }

    // Автоматическая загрузка уведомлений при загрузке страницы
    fetchNotifications();
});
