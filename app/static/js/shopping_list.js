document.addEventListener("DOMContentLoaded", function () {
    const searchBox = document.getElementById("search-box");
    const productItems = document.querySelectorAll(".product-item");

    // Реализация поиска продуктов
    searchBox.addEventListener("input", function () {
        const searchText = searchBox.value.trim().toLowerCase();
        productItems.forEach(item => {
            const productName = item.querySelector(".product-name").textContent.toLowerCase();
            if (productName.includes(searchText)) {
                item.style.display = "flex"; // Показываем найденный продукт
            } else {
                item.style.display = "none"; // Скрываем остальное
            }
        });
    });

    // Обработка кнопки "Добавить в корзину"
    document.querySelectorAll(".add-btn").forEach(button => {
        button.addEventListener("click", async function () {
            const productItem = this.closest("li");
            const productId = productItem.getAttribute("data-product-id");
            const addButton = this;

            try {
                const response = await fetch("/shopping_list/add", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        product_id: Number(productId),
                        count: 1 // Добавляем 1 продукт
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    // Заменяем кнопку на кнопки "-" и "+"
                    const controls = document.createElement("div");
                    controls.classList.add("quantity-controls");

                    const minusButton = document.createElement("button");
                    minusButton.textContent = "-";
                    minusButton.classList.add("quantity-btn", "decrease");
                    minusButton.addEventListener("click", () => updateQuantity(productId, -1, productItem));

                    const quantityDisplay = document.createElement("span");
                    quantityDisplay.textContent = "1";
                    quantityDisplay.classList.add("quantity-display");

                    const plusButton = document.createElement("button");
                    plusButton.textContent = "+";
                    plusButton.classList.add("quantity-btn", "increase");
                    plusButton.addEventListener("click", () => updateQuantity(productId, 1, productItem));

                    controls.appendChild(minusButton);
                    controls.appendChild(quantityDisplay);
                    controls.appendChild(plusButton);

                    productItem.replaceChild(controls, addButton);
                } else {
                    alert(result.error);
                }
            } catch (error) {
                alert("Произошла ошибка: " + error.message);
            }
        });
    });

    // Функция обновления количества
    async function updateQuantity(productId, change, productItem) {
        const quantityDisplay = productItem.querySelector(".quantity-display");
        let currentQuantity = Number(quantityDisplay.textContent);

        if (currentQuantity + change < 0) return; // Нельзя уменьшить ниже 0

        try {
            const response = await fetch("/shopping_list/update", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    product_id: Number(productId),
                    count: change // Передаем изменение количества
                })
            });

            const result = await response.json();

            if (response.ok) {
                currentQuantity += change;
                quantityDisplay.textContent = currentQuantity;

                // Если количество становится 0, возвращаем кнопку "Добавить в корзину"
                if (currentQuantity === 0) {
                    const addButton = document.createElement("button");
                    addButton.textContent = "Добавить в корзину";
                    addButton.classList.add("add-btn");
                    addButton.addEventListener("click", async function () {
                        const response = await fetch("/shopping_list/add", {
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
                            alert(result.message);
                            location.reload();
                        } else {
                            alert(result.error);
                        }
                    });
                    productItem.replaceChild(addButton, productItem.querySelector(".quantity-controls"));
                }
            } else {
                alert(result.error);
            }
        } catch (error) {
            alert("Произошла ошибка: " + error.message);
        }
    }
});
