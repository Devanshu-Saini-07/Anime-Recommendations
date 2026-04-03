from flask import Flask, render_template, request, redirect
from db_config import connect

app = Flask(__name__)

@app.route('/')
def home():
    status = request.args.get('status')  # get ?status= from URL
    db = connect()
    cursor = db.cursor()

    if status and status != "All":
        cursor.execute("SELECT * FROM Anime WHERE status=%s", (status,))
    else:
        cursor.execute("SELECT * FROM Anime")

    anime_list = cursor.fetchall()
    return render_template("index.html", anime_list=anime_list, selected_status=status)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        status = request.form['status']
        total_episodes = request.form['total_episodes']

        db = connect()
        cursor = db.cursor()
        query = "INSERT INTO Anime (title, genre, status, total_episodes) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (title, genre, status, total_episodes))
        db.commit()

        return redirect('/')
    return render_template("add.html")

@app.route('/details/<int:anime_id>')
def details(anime_id):
    db = connect()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Anime WHERE anime_id=%s", (anime_id,))
    anime = cursor.fetchone()
    return render_template("details.html", anime=anime)

@app.route('/recommendations')
def recommendations():
    db = connect()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Anime WHERE status='Completed'")
    recommendations = cursor.fetchall()
    return render_template("recommendations.html", recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)