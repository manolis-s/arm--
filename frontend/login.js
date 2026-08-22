const API_URL = "https://armex-q7rd.onrender.com";

document.getElementById("login-form").addEventListener("submit", async function(e){
    e.preventDefault()

    const username = document.getElementById("username").value
    const password = document.getElementById("password").value

    const messageDiv = document.getElementById("message")
    const loginBtn = document.getElementById("login-btn")

    loginBtn.disabled = true;
    loginBtn.textContent = "Σύνδεση..."
    messageDiv.textContent = ""

    const formData = new URLSearchParams()
    formData.append("username", username)
    formData.append("password", password)

    try{
        const response = await fetch(`${API_URL}/login`,{
            method: 'POST',
            headers:{"Content-Type": "application/x-www-form-urlencoded"},
            body: formData
        })

        const data = await response.json()

        if(response.ok){
            localStorage.setItem("token", data.access_token)

            window.location.href = "./index.html"
        } else{
            messageDiv.textContent = data.detail;
            messageDiv.className = "error";
            loginBtn.disabled = false;
            loginBtn.textContent = "Είσοδος";
        }
    } catch (error){
        messageDiv.textContent = "Πρόβλημα σύνδεσης με τον server.";
        messageDiv.className = "error";
        loginBtn.disabled = false;
        loginBtn.textContent = "Είσοδος"
    }

})