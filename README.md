# Armex (armέξ) - Military Expense Tracker

## About the Project
I initially built this application because I needed a way to track my daily expenses during my military service.

Because this is a common struggle for many soldiers, I designed the application to support multiple users. It features a full authentication system, meaning anyone can create their own account, log in securely, and manage their budget in private. It started as a personal tool, but it is fully functional and open for anyone else who might find it useful.

## Key Features
*   **Multi-User Support:** Secure registration and login system using JWT (JSON Web Tokens). Each user has their own private dashboard and data.
*   **Expense Tracking:** Add expenses and categorize them into "Inside Camp" and "Outside Camp" (with specific subcategories).
*   **Visual Analysis:** A dynamic donut chart that shows the ratio of money spent inside versus outside the camp.
*   **Recent Expenses:** A paginated list of recent transactions with the option to delete individual entries.
*   **Discharge Countdown:** A simple counter calculating the exact days remaining until the user's specific military discharge date.
*   **Protection Mechanisms:** Form submission freezing to prevent double entries on slow mobile networks.

## Technology Stack
*   **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
*   **Frontend:** HTML, CSS, Vanilla JavaScript
*   **External Libraries:** Chart.js (for graphs)
*   **Database:** PostgreSQL (hosted on Neon)

## Local Setup
If you want to run this project locally, follow these steps:

1. Clone the repository:
   git clone https://github.com/your-username/armex.git

2. Navigate to the project directory:
   cd armex

3. Install the required Python packages:
   pip install -r requirements.txt

4. Create a .env file in the root directory and add your secret key and database URL:
   SECRET_KEY="your_secret_key_here"
   DATABASE_URL="sqlite:///./armex.db" (or your PostgreSQL URL)

5. Run the FastAPI server:
   uvicorn main:app --reload

6. Open `index.html` in your browser or run a local live server for the frontend.
