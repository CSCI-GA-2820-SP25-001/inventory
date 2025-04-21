// Admin UI JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements for search functionality
    const searchBtn = document.getElementById('search-btn');
    const productIdInput = document.getElementById('product-id');
    const productDetails = document.getElementById('product-details');
    const errorMessage = document.getElementById('error-message');
    
    // Product detail elements
    const productName = document.getElementById('product-name');
    const productIdDisplay = document.getElementById('product-id-display');
    const productQuantity = document.getElementById('product-quantity');
    const productCondition = document.getElementById('product-condition');
    const productRestockLevel = document.getElementById('product-restock-level');
    const stockStatus = document.getElementById('stock-status');
    
    // Get DOM elements for add product functionality
    const addProductBtn = document.getElementById('add-product-btn');
    const newProductName = document.getElementById('new-product-name');
    const newProductQuantity = document.getElementById('new-product-quantity');
    const newProductCondition = document.getElementById('new-product-condition');
    const newProductRestockLevel = document.getElementById('new-product-restock-level');
    const addProductMessage = document.getElementById('add-product-message');
    
    // Get DOM elements for update product functionality
    const editProductBtn = document.getElementById('edit-product-btn');
    const updateProductSection = document.getElementById('update-product-section');
    const updateProductQuantity = document.getElementById('update-product-quantity');
    const updateProductCondition = document.getElementById('update-product-condition');
    const updateProductRestockLevel = document.getElementById('update-product-restock-level');
    const updateProductBtn = document.getElementById('update-product-btn');
    const cancelUpdateBtn = document.getElementById('cancel-update-btn');
    const updateProductMessage = document.getElementById('update-product-message');
    
    // Variable to store the current product ID being edited
    let currentProductId = null;
    
    // Add event listener to search button
    searchBtn.addEventListener('click', searchProduct);
    
    // Add event listener to add product button
    addProductBtn.addEventListener('click', addProduct);
    
    // Add event listener to edit product button
    editProductBtn.addEventListener('click', editProduct);
    
    // Add event listener to update product button
    updateProductBtn.addEventListener('click', updateProduct);
    
    // Add event listener to cancel update button
    cancelUpdateBtn.addEventListener('click', cancelUpdate);
    
    // Add event listener for Enter key on input field
    productIdInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            searchProduct();
        }
    });
    
    // Function to search for a product by ID
    function searchProduct() {
        // Get the product ID from the input
        const productId = productIdInput.value.trim();
        
        // Validate input
        if (!productId) {
            showError('Please enter a product ID');
            return;
        }
        
        // Clear previous results
        hideError();
        
        // Show loading state
        searchBtn.textContent = 'Searching...';
        searchBtn.disabled = true;
        
        // Fetch product data from API
        fetch(`/inventory/${productId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Product with ID ${productId} not found`);
                }
                return response.json();
            })
            .then(data => {
                displayProductDetails(data);
                searchBtn.textContent = 'Search';
                searchBtn.disabled = false;
            })
            .catch(error => {
                showError(error.message);
                productDetails.classList.add('hidden');
                searchBtn.textContent = 'Search';
                searchBtn.disabled = false;
            });
    }
    
    // Function to display product details
    function displayProductDetails(product) {
        // Update product details
        productName.textContent = product.name;
        productIdDisplay.textContent = product.id;
        productQuantity.textContent = product.quantity;
        productCondition.textContent = product.condition;
        productRestockLevel.textContent = product.restock_level;
        
        // Store the current product ID
        currentProductId = product.id;
        
        // Check stock status
        if (product.quantity < product.restock_level) {
            stockStatus.textContent = 'Low Stock Alert! Quantity is below restock level.';
            stockStatus.className = 'stock-status low-stock';
        } else {
            stockStatus.textContent = 'Stock level is adequate.';
            stockStatus.className = 'stock-status in-stock';
        }
        
        // Show product details
        productDetails.classList.remove('hidden');
        
        // Hide update section if it's visible
        updateProductSection.classList.add('hidden');
    }
    
    // Function to show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }
    
    // Function to hide error message
    function hideError() {
        errorMessage.textContent = '';
        errorMessage.classList.add('hidden');
    }
    
    // Function to add a new product
    function addProduct() {
        // Get form values
        const name = newProductName.value.trim();
        const quantity = newProductQuantity.value.trim();
        const condition = newProductCondition.value.trim();
        const restockLevel = newProductRestockLevel.value.trim();
        
        // Validate inputs
        if (!name || !quantity || !condition || !restockLevel) {
            showAddProductMessage('Please fill out all fields', false);
            return;
        }
        
        // Create product data object
        const productData = {
            name: name,
            quantity: parseInt(quantity),
            condition: condition,
            restock_level: parseInt(restockLevel)
        };
        
        // Show loading state
        addProductBtn.textContent = 'Adding...';
        addProductBtn.disabled = true;
        
        // Send POST request to API
        fetch('/inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to add product');
            }
            return response.json();
        })
        .then(data => {
            // Show success message
            showAddProductMessage(`Product "${data.name}" successfully added with ID: ${data.id}`, true);
            
            // Reset form
            newProductName.value = '';
            newProductQuantity.value = '';
            newProductCondition.value = '';
            newProductRestockLevel.value = '';
            
            // Reset button
            addProductBtn.textContent = 'Add Product';
            addProductBtn.disabled = false;
        })
        .catch(error => {
            // Show error message
            showAddProductMessage(error.message, false);
            
            // Reset button
            addProductBtn.textContent = 'Add Product';
            addProductBtn.disabled = false;
        });
    }
    
    // Function to show add product message
    function showAddProductMessage(message, isSuccess) {
        addProductMessage.textContent = message;
        addProductMessage.classList.remove('hidden', 'success', 'error');
        addProductMessage.classList.add(isSuccess ? 'success' : 'error');
        
        // Hide message after 5 seconds
        setTimeout(() => {
            addProductMessage.classList.add('hidden');
        }, 5000);
    }
    
    // Function to show update product message
    function showUpdateProductMessage(message, isSuccess) {
        updateProductMessage.textContent = message;
        updateProductMessage.classList.remove('hidden', 'success', 'error');
        updateProductMessage.classList.add(isSuccess ? 'success' : 'error');
        
        // Hide message after 5 seconds
        setTimeout(() => {
            updateProductMessage.classList.add('hidden');
        }, 5000);
    }
    
    // Function to handle edit product button click
    function editProduct() {
        if (!currentProductId) {
            showError('No product selected for editing');
            return;
        }
        
        // Populate update form with current values
        updateProductQuantity.value = productQuantity.textContent;
        updateProductCondition.value = productCondition.textContent;
        updateProductRestockLevel.value = productRestockLevel.textContent;
        
        // Show update section
        updateProductSection.classList.remove('hidden');
    }
    
    // Function to handle cancel update button click
    function cancelUpdate() {
        // Hide update section
        updateProductSection.classList.add('hidden');
    }
    
    // Function to handle update product button click
    function updateProduct() {
        if (!currentProductId) {
            showUpdateProductMessage('No product selected for updating', false);
            return;
        }
        
        // Get form values
        const quantity = updateProductQuantity.value.trim();
        const condition = updateProductCondition.value.trim();
        const restockLevel = updateProductRestockLevel.value.trim();
        
        // Validate inputs
        if (!quantity || !condition || !restockLevel) {
            showUpdateProductMessage('Please fill out all fields', false);
            return;
        }
        
        // Create product data object
        const productData = {
            name: productName.textContent, // Keep the existing name
            quantity: parseInt(quantity),
            condition: condition,
            restock_level: parseInt(restockLevel)
        };
        
        console.log('Updating product with data:', productData);
        
        // Show loading state
        updateProductBtn.textContent = 'Updating...';
        updateProductBtn.disabled = true;
        
        // Send PUT request to API
        fetch(`/inventory/${currentProductId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update product');
            }
            return response.json();
        })
        .then(data => {
            // Show success message
            showUpdateProductMessage(`Product "${data.name}" successfully updated`, true);
            
            console.log('Product updated successfully:', data);
            
            // Update the displayed product details
            displayProductDetails(data);
            
            // Reset button
            updateProductBtn.textContent = 'Update Product';
            updateProductBtn.disabled = false;
            
            // Hide update section
            updateProductSection.classList.add('hidden');
        })
        .catch(error => {
            // Show error message
            showUpdateProductMessage(error.message, false);
            console.error('Error updating product:', error);
            
            // Reset button
            updateProductBtn.textContent = 'Update Product';
            updateProductBtn.disabled = false;
        });
    }
});
