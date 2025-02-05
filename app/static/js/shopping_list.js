document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const productId = this.closest("li").getAttribute("data-product-id");
            deleteFromShoppingList(productId);
        });
    });

    document.querySelectorAll(".move-to-fridge-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const productId = this.closest("li").getAttribute("data-product-id");
            moveToFridge(productId);
        });
    });
});

async function deleteFromShoppingList(productId) {
    if (!confirm("Вы уверены, что хотите удалить этот продукт из списка покупок?")) return;

    const response = await fetch(`/shopping_list/delete/${productId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    });

    if (response.ok) {
        document.querySelector(`li[data-product-id='${productId}']`).remove();
    } else {
        alert("Ошибка при удалении товара.");
    }
}

async function moveToFridge(productId) {
    const response = await fetch(`/shopping_list/move_to_fridge/${productId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    });

    if (response.ok) {
        document.querySelector(`li[data-product-id='${productId}']`).remove();
        alert("Продукт перемещён в холодильник");
    } else {
        alert("Ошибка при перемещении товара.");
    }
}
