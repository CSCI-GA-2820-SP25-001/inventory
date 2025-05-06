document.addEventListener("DOMContentLoaded", () => {
    const viewBtn = document.getElementById("view-products-btn");
    const table = document.getElementById("products-table");
    const tbody = table.querySelector("tbody");

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
});
