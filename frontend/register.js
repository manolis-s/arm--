const API_URL = "https://armex-q7rd.onrender.com"
document.getElementById("register-form").addEventListener("submit", async function(e){
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const messageDiv = document.getElementById("message");
    const submitBtn = document.getElementById("register-btn");

    submitBtn.disabled = true;
    submitBtn.textContent = "Δημιουργία λογαριασμού...";
    messageDiv.textContent = "";
    
    try{
        const response = await fetch(`${API_URL}/register/`,{
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username: username,
                password: password
            })

        })

        const data = await response.json()
        if(response.ok){
            messageDiv= "Επιτυχής Συγγραφή! Μεταφορά στην σύνδεση..."
            messageDiv.className = "success"

            setTimeout(()=>{
                window.location.href = "./login.html";
            },1500)
        } else {
            messageDiv.textContent = data.detail;
            messageDiv.className = "error";
            submitBtn.disabled = false;
            submitBtn.textContent = "Εγγραφή";
        }
    } catch (error){
        messageDiv.textContent = "Πρόβλημα σύνδεσης με τον server.";
        messageDiv.className = "error";
        submitBtn.disabled = false;
        submitBtn.textContent = "Εγγραφή";
    }
})