document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('form');
    const usernameInput = document.querySelector('#username');
    const emailInput = document.querySelector('#email');
    const passwordInput = document.querySelector('#password');
    const confirmPasswordInput = document.querySelector('#confirm_password');
    const errorMessages = {
        username: "Имя пользователя должно быть уникальным.",
        email: "Введите правильный email.",
        password: "Пароль должен быть не менее 6 символов.",
        confirm_password: "Пароли не совпадают."
    };

    form.addEventListener('submit', function (event) {
        // Предотвращаем отправку формы для дальнейшей проверки
        event.preventDefault();
        
        // Проверяем валидность каждого поля
        let valid = true;

        if (!usernameInput.value) {
            showError(usernameInput, errorMessages.username);
            valid = false;
        }

        if (!emailInput.value || !emailInput.value.includes('@')) {
            showError(emailInput, errorMessages.email);
            valid = false;
        }

        if (passwordInput.value.length < 6) {
            showError(passwordInput, errorMessages.password);
            valid = false;
        }

        if (passwordInput.value !== confirmPasswordInput.value) {
            showError(confirmPasswordInput, errorMessages.confirm_password);
            valid = false;
        }

        if (valid) {
            form.submit(); // Если все поля валидны, отправляем форму
        }
    });

    // Функция для отображения ошибки под полем ввода
    function showError(input, message) {
        const errorElement = input.parentElement.querySelector('.error');
        if (!errorElement) {
            const errorDiv = document.createElement('div');
            errorDiv.classList.add('error');
            errorDiv.textContent = message;
            input.parentElement.appendChild(errorDiv);
        }
    }

    // Очистка ошибок при изменении значения в поле
    [usernameInput, emailInput, passwordInput, confirmPasswordInput].forEach(input => {
        input.addEventListener('input', function () {
            const errorElement = input.parentElement.querySelector('.error');
            if (errorElement) {
                errorElement.remove();
            }
        });
    });
});
