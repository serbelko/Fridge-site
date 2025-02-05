async function fetchProducts() {
    const response = await fetch('/api/products');
    const products = await response.json();
    const list = document.getElementById("product-list");
    list.innerHTML = "";

    products.forEach(product => {
        const li = document.createElement("li");
        li.textContent = `${product.product_name} (${product.product_type}) - Годен до: ${product.date_expiry}`;
        list.appendChild(li);
    });
}
