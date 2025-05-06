document.addEventListener("DOMContentLoaded", () => {
    // ===== Elements for all functionality =====
    const table = document.getElementById("products-table");
    const tbody = table?.querySelector("tbody");

    // ===== LIST + FILTER =====
    const viewBtn = document.getElementById("view-products-btn");
    const filterBtn = document.getElementById("filter-btn");
    const conditionSelect = document.getElementById("condition-filter");

    viewBtn?.addEventListener("click", () => fetchAndRenderInventory("/inventory"));
    filterBtn?.addEventListener("click", () => {
        const condition = conditionSelect.value;
        let url = "/inventory";
        if (condition) {
            url += `?condition=${condition}`;
        }
        fetchAndRenderInventory(url);
    });

    async function fetchAndRenderInventory(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch inventory");
            const data = await response.json();
            tbody.innerHTML = "";
            data.forEach(item => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.name}</td>
                    <td>${item.quantity}</td>
                    <td>${item.condition}</td>
                `;
                tbody.appendChild(row);
            });
            table.classList.remove("hidden");
        } catch (err) {
            alert("Error: " + err.message);
        }
    }

    // ===== SEARCH =====
    const searchBtn = document.getElementById('search-btn');
    const productIdInput = document.getElementById('product-id');
    const productDetails = document.getElementById('product-details');
    const errorMessage = document.getElementById('error-message');
    const productName = document.getElementById('product-name');
    const productIdDisplay = document.getElementById('product-id-display');
    const productQuantity = document.getElementById('product-quantity');
    const productCondition = document.getElementById('product-condition');
    const productRestockLevel = document.getElementById('product-restock-level');
    const stockStatus = document.getElementById('stock-status');

    searchBtn?.addEventListener('click', searchProduct);
    productIdInput?.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            searchProduct();
        }
    });

    function searchProduct() {
        const productId = productIdInput.value.trim();
        if (!productId) {
            showError('Please enter a product ID');
            return;
        }
        hideError();
        searchBtn.textContent = 'Searching...';
        searchBtn.disabled = true;

        fetch(`/inventory/${productId}`)
            .then(response => {
                if (!response.ok) throw new Error(`Product with ID ${productId} not found`);
                return response.json();
            })
            .then(data => {
                displayProductDetails(data);
            })
            .catch(error => {
                showError(error.message);
                productDetails.classList.add('hidden');
            })
            .finally(() => {
                searchBtn.textContent = 'Search';
                searchBtn.disabled = false;
            });
    }

    function displayProductDetails(product) {
        productName.textContent = product.name;
        productIdDisplay.textContent = product.id;
        productQuantity.textContent = product.quantity;
        productCondition.textContent = product.condition;
        productRestockLevel.textContent = product.restock_level;
        currentProductId = product.id;

        stockStatus.textContent = product.quantity < product.restock_level
            ? 'Low Stock Alert! Quantity is below restock level.'
            : 'Stock level is adequate.';
        stockStatus.className = product.quantity < product.restock_level
            ? 'stock-status low-stock'
            : 'stock-status in-stock';

        productDetails.classList.remove('hidden');
        updateProductSection.classList.add('hidden');
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }

    function hideError() {
        errorMessage.textContent = '';
        errorMessage.classList.add('hidden');
    }

    // ===== ADD PRODUCT =====
    const addProductBtn = document.getElementById('add-product-btn');
    const newProductName = document.getElementById('new-product-name');
    const newProductQuantity = document.getElementById('new-product-quantity');
    const newProductCondition = document.getElementById('new-product-condition');
    const newProductRestockLevel = document.getElementById('new-product-restock-level');
    const addProductMessage = document.getElementById('add-product-message');

    addProductBtn?.addEventListener('click', () => {
        const name = newProductName.value.trim();
        const quantity = newProductQuantity.value.trim();
        const condition = newProductCondition.value.trim();
        const restockLevel = newProductRestockLevel.value.trim();

        if (!name || !quantity || !condition || !restockLevel) {
            showAddProductMessage('Please fill out all fields', false);
            return;
        }

        const productData = {
            name,
            quantity: parseInt(quantity),
            condition,
            restock_level: parseInt(restockLevel)
        };

        addProductBtn.textContent = 'Adding...';
        addProductBtn.disabled = true;

        fetch('/inventory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(productData)
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to add product');
            return response.json();
        })
        .then(data => {
            showAddProductMessage(`Product "${data.name}" added with ID: ${data.id}`, true);
            newProductName.value = '';
            newProductQuantity.value = '';
            newProductCondition.value = '';
            newProductRestockLevel.value = '';
        })
        .catch(err => showAddProductMessage(err.message, false))
        .finally(() => {
            addProductBtn.textContent = 'Add Product';
            addProductBtn.disabled = false;
        });
    });

    function showAddProductMessage(message, isSuccess) {
        addProductMessage.textContent = message;
        addProductMessage.className = isSuccess ? 'message success' : 'message error';
        addProductMessage.classList.remove('hidden');
        setTimeout(() => addProductMessage.classList.add('hidden'), 5000);
    }

    // ===== UPDATE PRODUCT =====
    const editProductBtn = document.getElementById('edit-product-btn');
    const updateProductSection = document.getElementById('update-product-section');
    const updateProductQuantity = document.getElementById('update-product-quantity');
    const updateProductCondition = document.getElementById('update-product-condition');
    const updateProductRestockLevel = document.getElementById('update-product-restock-level');
    const updateProductBtn = document.getElementById('update-product-btn');
    const cancelUpdateBtn = document.getElementById('cancel-update-btn');
    const updateProductMessage = document.getElementById('update-product-message');
    let currentProductId = null;

    editProductBtn?.addEventListener('click', () => {
        if (!currentProductId) return showError('No product selected');
        updateProductQuantity.value = productQuantity.textContent;
        updateProductCondition.value = productCondition.textContent;
        updateProductRestockLevel.value = productRestockLevel.textContent;
        updateProductSection.classList.remove('hidden');
    });

    cancelUpdateBtn?.addEventListener('click', () => {
        updateProductSection.classList.add('hidden');
    });

    updateProductBtn?.addEventListener('click', () => {
        if (!currentProductId) return showUpdateProductMessage('No product selected', false);
        const quantity = updateProductQuantity.value.trim();
        const condition = updateProductCondition.value.trim();
        const restockLevel = updateProductRestockLevel.value.trim();

        if (!quantity || !condition || !restockLevel) {
            return showUpdateProductMessage('Please fill out all fields', false);
        }

        const productData = {
            name: productName.textContent,
            quantity: parseInt(quantity),
            condition,
            restock_level: parseInt(restockLevel)
        };

        updateProductBtn.textContent = 'Updating...';
        updateProductBtn.disabled = true;

        fetch(`/inventory/${currentProductId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(productData)
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to update product');
            return response.json();
        })
        .then(data => {
            showUpdateProductMessage(`Product "${data.name}" updated`, true);
            displayProductDetails(data);
            updateProductSection.classList.add('hidden');
        })
        .catch(err => showUpdateProductMessage(err.message, false))
        .finally(() => {
            updateProductBtn.textContent = 'Update Product';
            updateProductBtn.disabled = false;
        });
    });

    function showUpdateProductMessage(message, isSuccess) {
        updateProductMessage.textContent = message;
        updateProductMessage.className = isSuccess ? 'message success' : 'message error';
        updateProductMessage.classList.remove('hidden');
        setTimeout(() => updateProductMessage.classList.add('hidden'), 5000);
    }

    // ===== MARK AS DAMAGED =====
    const markDamagedBtn = document.getElementById("mark-damaged-btn");

    markDamagedBtn?.addEventListener("click", async () => {
        const productId = productIdDisplay.textContent;
        try {
            const response = await fetch(`/inventory/${productId}/mark_damaged`, {
                method: "PUT"
            });
            if (!response.ok) throw new Error("Failed to mark product as damaged");
            const updated = await response.json();
            productCondition.textContent = updated.condition;
            alert("Product marked as damaged.");
        } catch (err) {
            alert("Error marking product as damaged: " + err.message);
        }
    });
});

