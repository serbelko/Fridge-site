document.addEventListener("DOMContentLoaded", function () {
    // Получаем все ссылки в навигации
    const navLinks = document.querySelectorAll("nav ul li a");

    // Устанавливаем активную ссылку
    navLinks.forEach(link => {
        link.addEventListener("click", function () {
            navLinks.forEach(link => link.classList.remove("active"));
            this.classList.add("active");
        });
    });

    // Автоматически выделяем активную ссылку в зависимости от текущего URL
    const currentUrl = window.location.pathname;
    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentUrl) {
            link.classList.add("active");
        }
    });
});
