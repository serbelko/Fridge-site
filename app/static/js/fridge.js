document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            const productId = this.closest("li").getAttribute("data-product-id");
            deleteProduct(productId);
        });
    });
});


// Функция загрузки данных о продуктах
async function fetchProducts() {
    const response = await fetch('/fridge');
    const products = await response.json();
    const list = document.querySelector(".fridge-list");
    list.innerHTML = "";

    products.forEach(product => {
        const li = document.createElement("li");

        // Создаём индикатор срока годности
        const statusIndicator = document.createElement("div");
        statusIndicator.classList.add("status-indicator");

        const expirationDate = new Date(product.create_until);
        const today = new Date();
        const twoDaysBeforeExpiry = new Date();
        twoDaysBeforeExpiry.setDate(today.getDate() + 2);

        if (expirationDate < today) {
            statusIndicator.classList.add("expired");
        } else if (expirationDate <= twoDaysBeforeExpiry) {
            statusIndicator.classList.add("warning");
        } else {
            statusIndicator.classList.add("normal");
        }

        // Информация о товаре
        const productInfo = document.createElement("div");
        productInfo.classList.add("product-info");
        productInfo.innerHTML = `<strong>${product.name}</strong> (${product.product_type})<br>
                                 Количество: ${product.count}<br>
                                 Срок годности: ${product.create_from} → ${product.create_until}`;

        li.appendChild(statusIndicator);
        li.appendChild(productInfo);
        list.appendChild(li);
    });

async function deleteProduct(productId) {
    if (!confirm("Вы уверены, что хотите удалить этот продукт?")) return;

    const response = await fetch(`/api/fridge/${productId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        }
    });

    const result = await response.json();

    if (response.ok) {
        alert(result.message);
        location.reload();  // Обновляем страницу, чтобы обновить список
    } else {
        alert(result.error);
    }
}

}

async function deleteProduct(productId) {
    if (!confirm("Вы уверены, что хотите удалить этот продукт?")) return;

    const response = await fetch(`/api/fridge/${productId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        }
    });

    const result = await response.json();

    if (response.ok) {
        alert(result.message);
        location.reload();  // Перезагружаем страницу после удаления
    } else {
        alert(result.error);
    }
}