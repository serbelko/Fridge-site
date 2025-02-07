document.addEventListener("DOMContentLoaded", async function () {
    const video = document.getElementById("scanner");
    const startScanBtn = document.getElementById("start-scan");
    const scanQrBtn = document.getElementById("scan-qr");
    const productInfo = document.getElementById("product-info");
    const addToFridgeBtn = document.getElementById("add-to-fridge");
    const cancelBtn = document.getElementById("cancel");
    const scannerContainer = document.getElementById("scanner-container");

    let stream = null; // Видеопоток
    let productData = null;
    let userId = null;

    // Получение user_id
    async function getUserId() {
        try {
            const response = await fetch('/get_user_id');
            const data = await response.json();
            console.log("User ID from API:", data.user_id);
            userId = data.user_id;  // Сохраняем user_id
        } catch (error) {
            console.error("Ошибка получения user_id:", error);
        }
    }

    await getUserId();  // Загружаем user_id сразу

    // --- Проверяем поддержку камеры ---
    async function checkCameraAccess() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Ваш браузер не поддерживает доступ к камере.");
            return false;
        }
        return true;
    }

    // --- Включение камеры ---
    async function startCamera() {
        if (!(await checkCameraAccess())) return;

        try {
            const constraints = {
                video: {
                    facingMode: { ideal: "environment" }, // Задняя камера на телефонах
                    width: { ideal: 1280 }, 
                    height: { ideal: 720 }
                }
            };

            stream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = stream;
            video.setAttribute("playsinline", true); // Для работы в мобильных браузерах
            video.play();

            startScanBtn.style.display = "none";
            scanQrBtn.style.display = "block";
        } catch (error) {
            console.error("Ошибка доступа к камере:", error);
            alert("Ошибка доступа к камере: " + error.message);
        }
    }

    startScanBtn.addEventListener("click", startCamera);

    // --- Сканирование QR-кода ---
    scanQrBtn.addEventListener("click", async function () {
        if (!video.videoWidth) {
            alert("Ошибка: камера не активна.");
            return;
        }

        try {
            const canvas = document.createElement("canvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageData = canvas.toDataURL("image/png");

            const response = await fetch("/scan_qr_camera", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image: imageData })
            });

            const result = await response.json();
            if (response.ok) {
                productData = result;
                console.log("Данные товара:", productData);
                showProductInfo();
            } else {
                console.error("Ошибка сервера:", result.error);
                alert(result.error);
            }
        } catch (error) {
            console.error("Ошибка при обработке QR-кода:", error);
            alert("Ошибка при обработке QR-кода. Попробуйте ещё раз.");
        }
    });

    // --- Отображение данных о товаре ---
    function showProductInfo() {
        if (!productData) {
            alert("Ошибка: данные товара не найдены.");
            return;
        }

        // Проверка обязательных данных
        if (!productData.create_from) {
            alert("Ошибка: отсутствует дата производства продукта!");
            return;
        }

        if (!productData.create_until) {
            alert("Ошибка: отсутствует срок годности продукта!");
            return;
        }

        productInfo.style.display = "block";
        scannerContainer.style.display = "none"; // Скрываем камеру
    }

    // --- Добавление в холодильник ---
    addToFridgeBtn.addEventListener("click", async function () {
        console.log("Отправляем данные на сервер:", productData);

        try {
            const response = await fetch("/fridge/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    product_id: productData.product_id,
                    create_from: productData.create_from.split(" ")[0],
                    create_until: productData.create_until.split(" ")[0],
                    count: productData.count,
                    user_id: userId // Используем user_id, полученное ранее
                })
            });

            const result = await response.json();

            if (response.ok) {
                alert("Продукт добавлен в холодильник!");
                location.reload();
            } else {
                console.error("Ошибка добавления:", result.error);
                alert(result.error);
            }
        } catch (error) {
            console.error("Ошибка при добавлении продукта:", error);
            alert("Ошибка при добавлении продукта. Попробуйте ещё раз.");
        }
    });

    // --- Отмена сканирования ---
    cancelBtn.addEventListener("click", function () {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        location.reload();
    });
});
