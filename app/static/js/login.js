document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('form');
    const emailInput = document.querySelector('#email');
    const passwordInput = document.querySelector('#password');
    const errorMessages = {
        email: "Введите корректный email.",
        password: "Пароль не может быть пустым."
    };

    form.addEventListener('submit', function (event) {
        event.preventDefault();  // Отменяем стандартное поведение отправки формы

        let valid = true;

        // Проверка поля email
        if (!emailInput.value || !emailInput.value.includes('@')) {
            showError(emailInput, errorMessages.email);
            valid = false;
        }

        // Проверка поля пароля
        if (!passwordInput.value) {
            showError(passwordInput, errorMessages.password);
            valid = false;
        }

        if (valid) {
            form.submit();  // Если все поля валидны, отправляем форму
        }
    });

    // Функция для отображения ошибки
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
    [emailInput, passwordInput].forEach(input => {
        input.addEventListener('input', function () {
            const errorElement = input.parentElement.querySelector('.error');
            if (errorElement) {
                errorElement.remove();
            }
        });
    });
});
