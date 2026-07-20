const apiUrl = "http://127.0.0.1:8000";

// --- STATE MANAGEMENT TRACKER ---
let editingTransactionId = null;

// --- DELETE PIPELINE ---
async function deleteTransaction(id) {
    if (!confirm("Are you sure you want to delete this transaction?")) return;

    try {
        const response = await fetch(`${apiUrl}/transactions/${id}`, {
            method: "DELETE"
        });

        if (response.ok) {
            loadTransaction();
            loadFinancialSummary();
        } else {
            alert("Failed to delete the record.");
        }
    } catch (error) {
        console.error("Error communicating with delete API:", error);
    }
}

// --- EDIT INITIATION PHASE ---
function editTransaction(id, date, description, category, amount) {
    editingTransactionId = id;

    // Load data values back into the HTML elements
    document.getElementById("date").value = date;
    document.getElementById("description").value = description;
    document.getElementById("category").value = category;
    document.getElementById("amount").value = Math.abs(amount);

    // Provide visual styling changes to the UI submit button
    const submitBtn = document.querySelector("#transactionForm button[type='submit']");
    submitBtn.textContent = "Save Changes";
    submitBtn.style.backgroundColor = "#0d6efd";
}

// --- MAIN LOAD FUNCTION ---
async function loadTransaction(searchTerm = "") {
    let url = `${apiUrl}/transactions`;
    if (searchTerm) {
        url += `?search=${encodeURIComponent(searchTerm)}`;
    }

    const response = await fetch(url);
    const data = await response.json();

    const tableBody = document.getElementById("transactionTableBody");
    tableBody.innerHTML = "";


    data.forEach(tx => {
        const row = document.createElement("tr");

        const absoluteAmount = Math.abs(tx.amount).toFixed(2);
        const isExpense = tx.amount < 0;
        const displayPrice = isExpense ? `-£${absoluteAmount}` : `£${absoluteAmount}`;
        const colorClass = isExpense ? "text-danger" : "text-success";

        // Escaping quote strings to prevent raw HTML syntax crash injection bugs
        const cleanDesc = tx.description.replace(/'/g, "\\'");
        const cleanCat = tx.category.replace(/'/g, "\\'");

        row.innerHTML = `
            <td>${tx.id}</td>
            <td>${tx.date}</td>
            <td>${cleanDesc}</td>
            <td>${cleanCat}</td>
            <td class="${colorClass}" style="font-weight: bold;">${displayPrice}</td>
            <td>
                <button onclick="editTransaction(${tx.id}, '${tx.date}', '${cleanDesc}', '${cleanCat}', ${tx.amount})" style="color: white; background-color: #ffc107; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; margin-right: 4px;">
                    Edit
                </button>
                <button onclick="deleteTransaction(${tx.id})" style="color: white; background-color: #dc3545; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer;">
                    Delete
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });
}

// --- INITIAL DATA INVOCATIONS ---
loadTransaction();
loadFinancialSummary();

// --- FORM SUBMISSION PIPELINE ---
const transactionForm = document.getElementById("transactionForm");

transactionForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const amount = document.getElementById("amount").value;
    const description = document.getElementById("description").value;
    const category = document.getElementById("category").value;
    const date = document.getElementById("date").value;

    const transactionPayload = {
        amount: parseFloat(amount),
        description: description,
        category: category,
        date: date
    };

    // Train Track Router Switch
    let url = `${apiUrl}/transactions`;
    let method = "POST";

    if (editingTransactionId !== null) {
        url = `${apiUrl}/transactions/${editingTransactionId}`;
        method = "PUT";
    }

    try {
        // Fixed: Swapped hardcoded strings with dynamic "url" and "method" variables
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(transactionPayload)
        });

        if (response.ok) {
            transactionForm.reset();

            // Clean up the tracking state back to normal
            editingTransactionId = null;
            const submitBtn = document.querySelector("#transactionForm button[type='submit']");
            submitBtn.textContent = "Add Transaction";
            submitBtn.style.backgroundColor = "";

            loadTransaction();
            loadFinancialSummary();
        }
    } catch (error) {
        console.error("Error sending data to backend:", error);
    }
});

// --- AGGREGATION PIPELINE ---
async function loadFinancialSummary() {
    try{
    // hit high-performance aggregation end-point
    const response = await fetch(`${apiUrl}/transactions/summary`);
    const summary = await response.json();

    // format the numbers safely into local currencies
    const formattedIncome = `£${Math.abs(summary.total_income).toFixed(2)}`;
    const formattedExpenses = `£${Math.abs(summary.total_expenses).toFixed(2)}`;

        // Net balance can be negative, so keep the minus sign if it dips below zero
        const netSign = summary.net_balance < 0 ? "-£" : "£";
        const formattedNet = `${netSign}${Math.abs(summary.net_balance).toFixed(2)}`;

        // 3. Inject the calculations directly into the DOM elements
        document.getElementById("totalIncome").textContent = formattedIncome;
        document.getElementById("totalExpenses").textContent = formattedExpenses;

        const netElement = document.getElementById("netBalance");
        netElement.textContent = formattedNet;

        // Visual cue: Turn net balance red if they are overspending, green if they are saving
        if (summary.net_balance < 0) {
            netElement.style.color = "#dc3545"; // Red
        } else {
            netElement.style.color = "#28a745"; // Green
        }

    } catch (error) {
        console.error("Error computing financial aggregates:", error);
    }
}

// --- LIVE SEARCH REAL-TIME FILTER ---
const tableSearch = document.getElementById("tableSearch");

tableSearch.addEventListener("input", (event) => {
    const textTyped = event.target.value;
    // Instantly query the backend and repaint the table on every single keystroke!
    loadTransaction(textTyped);
});