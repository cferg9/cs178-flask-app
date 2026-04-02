# dbCode.py
# Author: Your Name
# Helper functions for database connection and queries


import pymysql
import boto3
import uuid
from boto3.dynamodb.conditions import Key
import creds  # Make sure creds.py exists for MySQL access

# 1. Establish the resource once
# Make sure this region matches where you created the table!
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# 2. Define your table variables clearly
favorites_table = dynamodb.Table('Favorites')
table = dynamodb.Table('Notes') # Use a specific name like notes_table
# ----------------------------
# MySQL Helpers
# ----------------------------

def get_conn():
    """Returns a connection to the MySQL RDS instance."""
    conn = pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db,
        port = 3306, 
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def execute_query(query, args=()):
    """Executes a SELECT query and returns all rows as a list of dictionaries."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ----------------------------
# DynamoDB Helpers
# ----------------------------



def get_favorites():
    """Returns all items from the Favorites DynamoDB table."""
    try:
        response = favorites_table.scan()
        return response.get('Items', [])
    except Exception as e:
        print("Error fetching favorites:", e)
        return []

def add_favorite(user, country):
    """Adds a new favorite country for a user."""
    try:
        favorites_table.put_item(
            Item={
                'User': user,
                'Country': Country
            }
        )
        return True
    except Exception as e:
        print("Error adding favorite:", e)
        return False


# -------------------------
# CREATE NOTE
# -------------------------
def add_note_db(country_code, note):
    try:
        note_id = str(uuid.uuid4())
        notes_table.put_item(
            Item={
                'id': note_id,            # Check: Is your Partition Key actually named 'id'?
                'country_code': country_code,
                'note': note
            }
        )
        return True
    except Exception as e:
        print(f"Error: {e}") # This will tell you EXACTLY why it's failing
        return False


# -------------------------
# READ NOTES
# -------------------------
def get_notes_db():
    # Force the connection inside the function to see exactly what's wrong
    try:
        test_db = boto3.resource('dynamodb', region_name='us-east-1')
        test_table = test_db.Table('Notes') 
        response = test_table.scan()
        return response.get('Items', [])
    except Exception as e:
        # This will print the REAL reason (Permissions? Wrong Region? Table Name?)
        print(f"DEBUG ERROR: {e}")
        return []


# -------------------------
# UPDATE NOTE
# -------------------------
def update_note_db(note_id, new_note):
    table.update_item(
        Key={'id': note_id},
        UpdateExpression="set note = :n",
        ExpressionAttributeValues={
            ':n': new_note
        }
    )


# -------------------------
# DELETE NOTE
# -------------------------
def delete_note_db(note_id):
    table.delete_item(
        Key={'id': note_id}
    )