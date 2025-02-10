document.addEventListener("DOMContentLoaded", function () {
    // Обработчик кнопок "Удалить"
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            const productItem = this.closest("li");
            const productId = productItem.getAttribute("data-product-id");
            const deleteButton = this;

            // Заменяем кнопку на контроллеры количества
            replaceWithQuantityControls(productItem, productId);
        });
    });

    // Обработчик кнопок перемещения в холодильник
    document.querySelectorAll(".move-to-fridge-btn").forEach(button => {
        button.addEventListener("click", async function () {
            const productItem = this.closest("li");
            const productId = productItem.getAttribute("data-product-id");

            try {
                const response = await fetch("/fridge/add", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        product_id: Number(productId),
                        count: 1
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    alert("Продукт перемещен в холодильник!");
                    productItem.remove(); // Удаляем из списка покупок после перемещения
                } else {
                    alert(result.error);
                }
            } catch (error) {
                alert("Ошибка при перемещении: " + error.message);
            }
        });
    });

    // Функция замены кнопки "Удалить" на контроллер количества
    function replaceWithQuantityControls(productItem, productId) {
        const controls = document.createElement("div");
        controls.classList.add("quantity-controls");

        const minusButton = document.createElement("button");
        minusButton.textContent = "-";
        minusButton.classList.add("quantity-btn", "decrease");
        minusButton.addEventListener("click", () => updateQuantity(productItem, -1));

        const quantityDisplay = document.createElement("span");
        quantityDisplay.textContent = "1";
        quantityDisplay.classList.add("quantity-display");

        const plusButton = document.createElement("button");
        plusButton.textContent = "+";
        plusButton.classList.add("quantity-btn", "increase");
        plusButton.addEventListener("click", () => updateQuantity(productItem, 1));

        const confirmButton = document.createElement("button");
        confirmButton.textContent = "✔";
        confirmButton.classList.add("confirm-btn");
        confirmButton.addEventListener("click", () => applyChange(productId, productItem));

        controls.appendChild(minusButton);
        controls.appendChild(quantityDisplay);
        controls.appendChild(plusButton);
        controls.appendChild(confirmButton);

        productItem.replaceChild(controls, productItem.querySelector(".delete-btn"));
    }

    // Функция обновления количества
    function updateQuantity(productItem, change) {
        const quantityDisplay = productItem.querySelector(".quantity-display");
        let currentQuantity = Number(quantityDisplay.textContent);

        if (currentQuantity + change >= 1) { // Минимальное значение - 1
            quantityDisplay.textContent = currentQuantity + change;
        }
    }

    // Функция применения изменений
    async function applyChange(productId, productItem) {
        const quantityDisplay = productItem.querySelector(".quantity-display");
        let count = Number(quantityDisplay.textContent);

        try {
            const response = await fetch("/shopping_list/remove", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    product_id: Number(productId),
                    count: count // Удаляем только указанное количество
                })
            });

            const result = await response.json();

            if (response.ok) {
                // Обновляем количество в интерфейсе
                const productCountElement = productItem.querySelector(".product-info");
                let currentCount = parseInt(productCountElement.textContent.match(/\d+/)[0]);

                if (currentCount - count > 0) {
                    productCountElement.innerHTML = productCountElement.innerHTML.replace(
                        /\d+/, 
                        currentCount - count
                    );
                    
                    // Восстанавливаем кнопку "Удалить"
                    const deleteButton = document.createElement("button");
                    deleteButton.textContent = "🗑️ Удалить";
                    deleteButton.classList.add("delete-btn");
                    deleteButton.addEventListener("click", function () {
                        replaceWithQuantityControls(productItem, productId);
                    });

                    productItem.replaceChild(deleteButton, productItem.querySelector(".quantity-controls"));
                } else {
                    productItem.remove(); // Полностью удаляем продукт, если count = 0
                }
            } else {
                alert(result.error);
            }
        } catch (error) {
            alert("Ошибка при обновлении: " + error.message);
        }
    }
});
