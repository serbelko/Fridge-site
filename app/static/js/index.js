document.addEventListener("DOMContentLoaded", function () {
    const menuLinks = document.querySelectorAll(".menu li a");

    menuLinks.forEach(link => {
        link.addEventListener("mouseenter", function () {
            link.style.transform = "scale(1.05)";  // Добавляем анимацию при наведении
        });

        link.addEventListener("mouseleave", function () {
            link.style.transform = "scale(1)";  // Восстанавливаем после наведения
        });
    });
});
