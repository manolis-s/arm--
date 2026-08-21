if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js')
            .then(reg => console.log('Το Service Worker τρέχει! Scope:', reg.scope))
            .catch(err => console.error('Σφάλμα Service Worker:', err));
    });
}


const API_URL = "https://armex-q7rd.onrender.com";
let expenseChart = null

let categoriesData = []

function updateLeledometro() {
    // Ψάχνει αν έχεις αποθηκεύσει ημερομηνία. Αν όχι, βάζει την default.
    let savedDate = localStorage.getItem("dischargeDate");
    if (!savedDate) {
        savedDate = "2027-09-02";
    }

    const dischargeDate = new Date(savedDate);
    const today = new Date();

    const diffTime = dischargeDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    const daysLeftElement = document.getElementById("days-left");
    if (diffDays > 0) {
        daysLeftElement.textContent = diffDays;
    } else if (diffDays === 0) {
        daysLeftElement.textContent = "ΣΗΜΕΡΑ";
    } else {
        daysLeftElement.textContent = "Απολύθηκες";
    }
}


let selectedCategoryId = null


document.addEventListener("DOMContentLoaded", ()=>{
    fetchCategories();
    fetchStats()
    updateLeledometro()
    fetchRecentExpenses()

    const categorySelect = document.getElementById("category-select")
    const subcategorySelect = document.getElementById("subcategory-select")

    categorySelect.addEventListener("change", (event)=>{
        selectedCategoryId = parseInt(event.target.value)
        console.log("Επιλεγμένη κατηγορία:", selectedCategoryId)

        subcategorySelect.disabled = false;
        subcategorySelect.innerHTML = '<option value="" disabled selected>Επίλεξε...</option>';
        
        const selectedCategory = categoriesData.find(cat => cat.id === selectedCategoryId)
        if(selectedCategory && selectedCategory.subcategories){
            selectedCategory.subcategories.forEach(sub=>{
                const option = document.createElement("option")
                option.value = sub.id;
                option.textContent = sub.name
                subcategorySelect.appendChild(option)
            })
        } else{
            console.warn("Δεν βρέθηκαν υποκατηγορίες για την επιλεγμένη κατηγορία.")
        }
    })
})

async function fetchCategories(){
    try{
        const response = await fetch(`${API_URL}/categories/`)
        categoriesData = await response.json()

        const categorySelect = document.getElementById("category-select")

        categoriesData.forEach(cat => {
            const option = document.createElement("option")
            option.value = cat.id 
            option.textContent = cat.name;
            categorySelect.appendChild(option)
        });
    } catch (error){
        console.error('Σφάλμα φόρτωσης κατηγοριών', error)

    }
}

async function fetchStats() {
    try {
        const response = await fetch(`${API_URL}/stats/`);
        const stats = await response.json();

        // 1. Αποθηκεύουμε τα νούμερα σε μεταβλητές (και βάζουμε το || 0 για ασφάλεια αν είναι άδεια η βάση)
        const grandTotal = stats.grand_total || 0;
        const insideTotal = stats.camp_ratio.inside_camp || 0;
        const outsideTotal = stats.camp_ratio.outside_camp || 0;

        // 2. Ενημερώνουμε την πάνω κάρτα (στο Header)
        document.getElementById("grand-total").textContent = `${grandTotal.toFixed(2)} €`;
        document.getElementById("inside-total").textContent = `${insideTotal.toFixed(2)} €`;
        document.getElementById("outside-total").textContent = `${outsideTotal.toFixed(2)} €`;

        // 3. Ενημερώνουμε την κάτω κάρτα (στην Ανάλυση Εξόδων)
        document.getElementById("analysis-inside-total").textContent = `${insideTotal.toFixed(2)} €`;
        document.getElementById("analysis-outside-total").textContent = `${outsideTotal.toFixed(2)} €`;

        // 4. Ζωγραφίζουμε το γράφημα!
        updateChart(insideTotal, outsideTotal);

    } catch (error) {
        console.error("Σφάλμα φόρτωσης στατιστικών:", error);
    }
}

const expenseForm = document.getElementById("expense-form")

expenseForm.addEventListener("submit", async (event)=>{
    event.preventDefault()
    
    const amountValue = parseFloat(document.getElementById("amount").value)
    const subcategoryIdValue = parseInt(document.getElementById("subcategory-select").value)
    const descriptionValue = document.getElementById("description").value

    const expenseData = {
        amount: amountValue,
        subcategory_id: subcategoryIdValue,
        description: descriptionValue
    }

    try{
        const response = await fetch(`${API_URL}/expenses/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(expenseData)
        })
        if(response.ok){
            alert("Η καταχώρηση εξόδου ήταν επιτυχής!")
            window.location.reload
        }
    } catch (error) {
        console.error("Σφάλμα καταχώρησης εξόδου:", error)
    }
})

//prosfata eksoda//
async function fetchRecentExpenses(){
    try{
        const response = await fetch(`${API_URL}/expenses/recent`)
        const expenses = await response.json()

        const recentList = document.getElementById("recent-list")
        recentList.innerHTML = ""
        if(expenses.length ==0){
            recentList.innerHTML = '<li class="empty-msg" style="text-align:center; padding:10px; color:gray;">Δεν έχεις καταγράψει ακόμα έξοδα.</li>'
            return;
        }
        expenses.forEach(exp=>{
            const li = document.createElement("li")
            li.style.display = "flex"
            li.style.justifyContent = 'space-between'
            li.style.padding = '12px 0'
            li.style.borderBottom = '1px solid #eee'

            li.innerHTML = `
                <div>
                    <strong style="color: #2c3e50;">${exp.subcategory}</strong> 
                    <small style="color: gray;">(${exp.category})</small>
                    <br>
                    <small style="color: #888; font-size:12px;">${exp.date}</small>
                </div>
                <div style="color: #4b5320; font-weight: bold; font-size: 16px; display: flex; align-items: center;">
                    ${exp.amount.toFixed(2)} €
                </div>
            `;

            recentList.appendChild(li)
        })
    } catch (error){
        console.error("Σφάλμα φόρτωσης πρόσφατων εξόδων", error)
    }
}

// --- ΓΡΑΦΗΜΑ CHART.JS ---
function updateChart(insideAmount, outsideAmount) {
    const ctx = document.getElementById('myChart');

    // Αν υπάρχει ήδη γράφημα (από προηγούμενη φόρτωση), το καταστρέφουμε για να βάλουμε το νέο
    if (expenseChart !== null) {
        expenseChart.destroy();
    }

    // Φτιάχνουμε το νέο γράφημα τύπου "ντόνατ"
    expenseChart = new Chart(ctx, {
        type: 'doughnut', 
        data: {
            labels: ['Μέσα στο Στρατόπεδο', 'Έξω (Εξοδούχος)'],
            datasets: [{
                data: [insideAmount, outsideAmount],
                backgroundColor: [
                    '#4b5320', // Χακί για μέσα
                    '#1f2937'  // Σκούρο γκρι/μπλε για έξω
                ],
                borderWidth: 2,
                borderColor: '#ffffff' // Άσπρο περίγραμμα για να ξεχωρίζουν
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom', // Η λεζάντα να μπει από κάτω
                }
            }
        }
    });
}

// --- ΑΛΛΑΓΗ ΗΜΕΡΟΜΗΝΙΑΣ (Μολυβάκι) ---
document.getElementById("edit-date-btn").addEventListener("click", () => {
    let currentSaved = localStorage.getItem("dischargeDate") || "2027-09-02";
    // Ζητάμε από τον χρήστη να γράψει τη νέα
    let newDate = prompt("Βάλε τη νέα ημερομηνία απόλυσης (Μορφή: ΕΕΕΕ-ΜΜ-ΗΗ):", currentSaved);
    
    if (newDate) {
        // Ελέγχουμε αν είναι όντως ημερομηνία
        if (!isNaN(new Date(newDate).getTime())) {
            localStorage.setItem("dischargeDate", newDate); // Αποθήκευση στο κινητό
            updateLeledometro(); // Ανανέωση του αριθμού αμέσως
        } else {
            alert("Λάθος μορφή ημερομηνίας! Πρέπει να είναι ΕΕΕΕ-ΜΜ-ΗΗ.");
        }
    }
});

// --- ΔΙΑΓΡΑΦΗ ΟΛΩΝ ΤΩΝ ΕΞΟΔΩΝ ---
document.getElementById("delete-all-btn").addEventListener("click", async () => {
    // Επιβεβαίωση για να μην πατηθεί κατά λάθος
    if (confirm("ΕΙΣΑΙ ΣΙΓΟΥΡΟΣ; Θα διαγραφούν ΟΛΑ τα έξοδα οριστικά! Δεν υπάρχει επιστροφή.")) {
        try {
            const response = await fetch(`${API_URL}/expenses/all/`, {
                method: "DELETE" // Χρησιμοποιούμε τη μέθοδο DELETE
            });
            
            if (response.ok) {
                alert("Τα έξοδά σου διαγράφηκαν!");
                // Ανανεώνουμε τα στατιστικά και τη λίστα για να μηδενίσουν στην οθόνη
                fetchStats();
                fetchRecentExpenses();
            }
        } catch (error) {
            console.error("Σφάλμα διαγραφής:", error);
            alert("Κάτι πήγε στραβά κατά τη διαγραφή.");
        }
    }
});