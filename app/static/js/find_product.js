document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal");
    const closeModal = document.querySelector(".close");
    const addProductForm = document.getElementById("add-product-form");
    const searchBox = document.getElementById("search-box");
    const productItems = document.querySelectorAll(".product-item");

    // Поиск товаров в реальном времени
    searchBox.addEventListener("input", function () {
        const searchText = searchBox.value.trim().toLowerCase();
        productItems.forEach(item => {
            const productName = item.querySelector(".product-name").textContent.toLowerCase();
            if (productName.includes(searchText)) {
                item.style.display = "flex"; // Показываем товар
            } else {
                item.style.display = "none"; // Скрываем товар
            }
        });
    });

    document.querySelectorAll(".add-btn").forEach(button => {
        button.addEventListener("click", function () {
            const productId = this.closest("li").getAttribute("data-product-id");
            console.log("Выбран product_id:", productId); // Лог для отладки
            document.getElementById("selected-product-id").value = productId;
            modal.style.display = "block";
        });
    });

    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    addProductForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        
        const productId = document.getElementById("selected-product-id").value;
        const createFrom = document.getElementById("create-from").value;
        const createUntil = document.getElementById("create-until").value;

        // Формируем данные в виде массива объектов
        const dataToSend = [{
            product_id: Number(productId),
            create_from: createFrom.trim(),
            create_until: createUntil.trim(),
            count: 1
        }];

        const response = await fetch("/fridge/add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dataToSend) // Отправляем массив
        });

        console.log("Отправленные данные:", dataToSend); // Лог для отладки
        const result = await response.json();

        if (response.ok) {
            alert(result[0]?.message || "Продукт успешно добавлен!");
            modal.style.display = "none";
        } else {
            alert(result.error || "Произошла ошибка!");
        }
    });
});
