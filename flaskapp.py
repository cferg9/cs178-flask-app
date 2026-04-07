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
    """Fetches all favorite items from the DynamoDB table."""
    try:
        response = table.scan()
        return response.get('Items', [])
    except Exception as e:
        print(f"Error fetching favorites: {e}")
        return []

# -------------------------
# HOME: Landing Page
# -------------------------
@app.route('/')
def home():
    """Renders the main entry point of the World Explorer application."""
    return render_template('home.html')


# -------------------------
# READ: Countries List with Search
# -------------------------
@app.route('/countries')
def countries():
    """
    Displays a list of countries. 
    Implements a search filter if a query is provided; otherwise, shows the top 20 by population.
    """
    search_query = request.args.get('search', '')
    
    try:
        if search_query:
            # Modular Logic: Search for countries matching the user input
            sql = """
                SELECT Code, Name, Continent, Population
                FROM country
                WHERE Name LIKE %s
                ORDER BY Population DESC
            """
            rows = execute_query(sql, (f"%{search_query}%",))
        else:
            # Default view: Optimized query for top 20 largest nations
            sql = """
                SELECT Code, Name, Continent, Population
                FROM country
                ORDER BY Population DESC
                LIMIT 20
            """
            rows = execute_query(sql)
    except Exception as e:
        flash("Could not retrieve country list. Please check database connection.", "danger")
        print(f"SQL Error in /countries: {e}")
        rows = []
        
    return render_template('countries.html', rows=rows, search_query=search_query)


# -------------------------
# JOIN QUERY: Detailed View
# -------------------------
@app.route('/country/<code>')
def country_detail(code):
    """
    Uses a SQL JOIN to pull relational data from 'country' and 'city' tables.
    Also fetches associated language data for a specific country code.
    """
    try:
        # 1. Relational JOIN: Linking country to its capital city name
        country_info = execute_query("""
            SELECT country.Name, city.Name AS CapitalName, country.Population, country.Continent
            FROM country
            LEFT JOIN city ON country.Capital = city.ID
            WHERE country.Code = %s
        """, (code,))

        # 2. Filtering Cities: Get all urban centers belonging to this nation
        cities = execute_query("""
            SELECT Name, District, Population 
            FROM city 
            WHERE CountryCode = %s 
            ORDER BY Population DESC
        """, (code,))

        # 3. Filtering Languages: Get linguistic data for the nation
        languages = execute_query("""
            SELECT Language, IsOfficial, Percentage 
            FROM countrylanguage 
            WHERE CountryCode = %s 
            ORDER BY Percentage DESC
        """, (code,))

        return render_template('country_detail.html', 
                               country=country_info[0] if country_info else None, 
                               cities=cities, 
                               languages=languages)
    except Exception as e:
        print(f"Error loading country details for {code}: {e}")
        flash("Error loading country data.", "danger")
        return redirect(url_for('countries'))


# -------------------------
# CREATE/UPDATE/DELETE: DynamoDB Notes Logic
# -------------------------
@app.route('/add-note', methods=['GET', 'POST'])
def add_note():
    """Handles the creation of new country-specific notes."""
    if request.method == 'POST':
        try:
            code = request.form['country_code']
            note = request.form['note']
            add_note_db(code, note)
            flash("Note added successfully!", "success")
            return redirect(url_for('notes'))
        except KeyError:
            flash("Missing form data.", "warning")
        except Exception as e:
            print(f"Note Creation Error: {e}")
            flash("System error saving note.", "danger")

    return render_template('add_note.html')

@app.route('/update-note/<id>', methods=['GET', 'POST'])
def update_note(id):
    """Updates an existing note record in DynamoDB by its unique ID."""
    if request.method == 'POST':
        try:
            new_note = request.form.get('note') 
            update_note_db(id, new_note)
            flash("Note updated!", "info")
            return redirect(url_for('notes')) 
        except Exception as e:
            print(f"Update Error: {e}")
            flash("Could not update note.", "danger")

    return render_template('update_note.html', id=id)

@app.route('/delete-note/<note_id>')
def delete_note(note_id):
    """Performs a DeleteItem operation in DynamoDB based on the note ID."""
    try:
        delete_note_db(note_id) 
        flash("Note deleted!", "success")
    except Exception as e:
        print(f"Deletion Error: {e}")
        flash("Failed to delete note.", "danger")
    return redirect(url_for('notes'))


@app.route('/notes')
def notes():
    """Displays all notes currently stored in the DynamoDB table."""
    try:
        all_notes = get_notes_db() 
        return render_template('notes.html', rows=all_notes)
    except Exception as e:
        print(f"Read Error (Notes): {e}")
        return render_template('notes.html', rows=[])

# -------------------------
# DYNAMODB: FAVORITES Logic
# -------------------------
@app.route('/favorite/<code>')
def favorite(code):
    """Bookmarks a specific country as a favorite for the current user."""
    try:
        add_favorite("Guest", code)  
        flash(f"Added {code} to favorites!", "success")
    except Exception as e:
        print(f"Favorite Error: {e}")
        flash("Could not save favorite.", "danger")
    return redirect(url_for('favorites'))

@app.route('/favorites')
def favorites():
    """Renders the user's saved favorites list."""
    favs = get_favorites()
    return render_template('favorites.html', favs=favs)

if __name__ == '__main__':
    # Standard boilerplate for running the Flask development server
    app.run(host='0.0.0.0', port=8080, debug=True)
