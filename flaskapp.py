# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT
import boto3
from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
from dbCode import *
from dbCode import add_note_db, get_notes_db, update_note_db, delete_note_db

app = Flask(__name__)
app.secret_key = 'your_secret_key' # this is an artifact for using flash displays; 
                                   # it is required, but you can leave this alone


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
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

        add_note_db(code, note)

        flash("Note added!", "success")
        # CHANGE 'notes' TO 'notes_page'
        return redirect(url_for('notes_page')) 

    return render_template('add_note.html')

@app.route('/notes')
def notes():
    rows = get_notes_db()
    return render_template('notes.html', rows=rows)

@app.route('/update-note/<id>', methods=['GET', 'POST'])
def update_note(id):
    if request.method == 'POST':
        # 1. Get the new text from the form
        new_note = request.form.get('note') 
        
        # 2. Call the DB function (Make sure this matches your dbCode.py name)
    
        update_note_db(id, new_note)

        flash("Note updated!", "info")
        return redirect(url_for('notes_page')) 

    return render_template('update_note.html', id=id)

@app.route('/delete-note/<note_id>') # The variable is <note_id>
def delete_note(note_id):
    # Pass that specific variable to the DB function
    delete_note_db(note_id) 
    flash("Note deleted!", "success")
    return redirect(url_for('notes_page'))


@app.route('/notes')
def notes_page():
    all_notes = get_notes_db() 
    print(f"--- DEBUG: DynamoDB returned {len(all_notes)} notes ---")
    print(f"--- DATA CONTENT: {all_notes} ---")
    return render_template('notes.html', rows=all_notes)

# -------------------------
# DYNAMODB: FAVORITES
# -------------------------
@app.route('/favorite/<code>')
def favorite(code):
    add_favorite("Guest", code)  
    
    flash(f"Added {code} to favorites!", "success")
    return redirect(url_for('favorites'))


@app.route('/favorites')
def favorites():
    favs = get_favorites()
    return render_template('favorites.html', favs=favs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
