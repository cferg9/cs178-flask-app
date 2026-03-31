# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT
import boto3
from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
from dbCode import *

app = Flask(__name__)
app.secret_key = 'your_secret_key' # this is an artifact for using flash displays; 
                                   # it is required, but you can leave this alone


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Favorites')  # make sure this matches your table name

def get_favorites():
    response = table.scan()
    return response['Items']
# -------------------------
# HOME
# -------------------------
@app.route('/')
def home():
    return render_template('home.html')


# -------------------------
# READ: Countries (Checkpoint)
# -------------------------
@app.route('/countries')
def countries():
    rows = execute_query("""
        SELECT Code, Name, Continent, Population
        FROM country
        ORDER BY Population DESC
        LIMIT 20
    """)
    return render_template('countries.html', rows=rows)


# -------------------------
# JOIN QUERY
# -------------------------
@app.route('/country/<code>')
def country_detail(code):
    rows = execute_query("""
        SELECT country.Name, city.Name, country.Population, country.Continent
        FROM country
        JOIN city ON country.Capital = city.ID
        WHERE country.Code = %s
    """, (code,))
    return render_template('country_detail.html', rows=rows)


# -------------------------
# CREATE NOTE
# -------------------------
@app.route('/add-note', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        code = request.form['country_code']
        note = request.form['note']

        execute_query("""
            INSERT INTO notes (country_code, note)
            VALUES (%s, %s)
        """, (code, note))

        flash("Note added!", "success")
        return redirect(url_for('notes'))

    return render_template('add_note.html')


# -------------------------
# READ NOTES
# -------------------------
@app.route('/notes')
def notes():
    rows = execute_query("SELECT * FROM notes")
    return render_template('notes.html', rows=rows)


# -------------------------
# UPDATE NOTE
# -------------------------
@app.route('/update-note/<int:id>', methods=['GET', 'POST'])
def update_note(id):
    if request.method == 'POST':
        new_note = request.form['note']

        execute_query("""
            UPDATE notes
            SET note = %s
            WHERE id = %s
        """, (new_note, id))

        flash("Note updated!", "info")
        return redirect(url_for('notes'))

    return render_template('update_note.html', id=id)


# -------------------------
# DELETE NOTE
# -------------------------
@app.route('/delete-note/<int:id>')
def delete_note(id):
    execute_query("DELETE FROM notes WHERE id = %s", (id,))
    flash("Deleted!", "warning")
    return redirect(url_for('notes'))


# -------------------------
# DYNAMODB: FAVORITES
# -------------------------
@app.route('/favorite/<code>')
def favorite(code):
    add_favorite(code)  # DynamoDB function
    flash("Added to favorites!", "success")
    return redirect(url_for('countries'))


@app.route('/favorites')
def favorites():
    favs = get_favorites()
    return render_template('favorites.html', favs=favs)

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
