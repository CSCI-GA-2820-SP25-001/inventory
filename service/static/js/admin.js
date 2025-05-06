document.addEventListener("DOMContentLoaded", () => {
    const viewBtn = document.getElementById("view-products-btn");
    const table = document.getElementById("products-table");
    const filterBtn = document.getElementById("filter-btn");
    const conditionSelect = document.getElementById("condition-filter");
    const tbody = table.querySelector("tbody");

    filterBtn.addEventListener("click", async () => {
        const condition = conditionSelect.value;
        let url = "/inventory";
        if (condition) {
            url += `?condition=${condition}`;
        }

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch filtered inventory");
            const data = await response.json();

            // Clear existing rows
            tbody.innerHTML = "";

            // Populate rows
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

            // Show table
            table.classList.remove("hidden");
        } catch (err) {
            alert("Error filtering inventory: " + err.message);
        }
    });

    viewBtn.addEventListener("click", async () => {
        try {
            const response = await fetch("/inventory");
            if (!response.ok) throw new Error("Failed to fetch inventory");
            const data = await response.json();

            // Clear existing rows
            tbody.innerHTML = "";

            // Populate rows
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

            // Show table
            table.classList.remove("hidden");
        } catch (err) {
            alert("Error loading inventory: " + err.message);
        }
    });
    const markDamagedBtn = document.getElementById("mark-damaged-btn");

    markDamagedBtn.addEventListener("click", async () => {
        const productId = document.getElementById("product-id-display").textContent;

        try {
            const response = await fetch(`/inventory/${productId}/mark_damaged`, {
                method: "PUT",
            });

            if (!response.ok) throw new Error("Failed to mark product as damaged");
            const updated = await response.json();

            // Update the UI to reflect the new condition
            document.getElementById("product-condition").textContent = updated.condition;
            alert("Product marked as damaged.");
        } catch (err) {
            alert("Error marking product as damaged: " + err.message);
        }
    });

    
});
