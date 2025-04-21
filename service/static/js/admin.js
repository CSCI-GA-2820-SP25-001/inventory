// Admin UI JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
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
    
    // Add event listener to search button
    searchBtn.addEventListener('click', searchProduct);
    
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
});
