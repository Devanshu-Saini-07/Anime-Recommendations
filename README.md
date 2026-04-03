# Anime Recommendations Web App

A simple Flask + MySQL web application to manage your anime list, track details, and view recommendations.  
Built with **Python, Flask, MySQL, HTML, CSS**.

---

## 🚀 Features
- Add new anime with title, genre, status, and total episodes
- View anime list in a clean table with filters:
  - All
  - Watching
  - Completed
  - Plan to Watch
- Detailed view for each anime with progress bar and notes
- Recommendations page showing completed anime in a card layout
- Responsive design with modern CSS styling

---

## 🛠️ Tech Stack
- **Backend:** Python (Flask)
- **Database:** MySQL
- **Frontend:** HTML, CSS
- **Template Engine:** Jinja2

---

## 📂 Project Structure
Anime Recommendations/
│
├── server.py              # Flask backend<br>
├── db_config.py           # Database connection<br>
├── schema.sql             # Database schema<br>
│<br>
├── static/                # Static files (CSS, JS, images)<br>
│   └── style.css          # Styling<br>
│<br>
└── templates/             # HTML templates<br>
    ├── index.html         # Homepage (anime list + filters)<br>
    ├── add.html           # Add anime form<br>
    ├── details.html       # Anime details page<br>
    └── recommendations.html # Recommendations page<br>



## ⚙️ Setup Instructions

### 1. Clone the repository
git clone https://github.com/Devanshu-Saini-07/Anime-Recommendations.git<br>
cd anime-recommendations

### 2. Install dependencies
pip install flask mysql-connector-python

### 3. Setup MySQL database
mysql -u root -p < schema.sql

# Update db_config.py with your MySQL credentials:
def connect():<br>
    return mysql.connector.connect(<br>
        host="localhost",<br>
        user="root",<br>
        password="yourpassword",<br>
        database="anime_db"<br>
    )

### 4. Run the server
python server.py

# Open in browser:
http://127.0.0.1:5000/