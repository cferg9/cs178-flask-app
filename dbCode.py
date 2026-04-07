# dbCode.py
# Author: Your Name
# Helper functions for database connection and queries


import pymysql
import boto3
import uuid
from boto3.dynamodb.conditions import Key
import creds  # Make sure creds.py exists for MySQL access


dynamodb = boto3.resource('dynamodb', region_name='us-east-1') 

notes_table = dynamodb.Table('Notes') 
favorites_table = dynamodb.Table('Favorites')
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
    """
    Retrieves all records from the Favorites DynamoDB table.
    Returns: A list of dictionary items representing favorite countries.
    """
    try:
        # Scanning the table to get all user-favorited items
        response = favorites_table.scan()
        return response.get('Items', [])
    except Exception as e:
        print(f"DATABASE ERROR (get_favorites): {e}")
        return []

def add_favorite(user, country_code):
    """
    Adds a new entry to the Favorites table using a Partition Key (User) 
    and Sort Key (Country).
    """
    try:
        # Re-initializing table reference to ensure it's active
        table = dynamodb.Table('Favorites')
        table.put_item(
            Item={
                'User': user,          # Partition Key
                'Country': country_code # Sort Key
            }
        )
        return True
    except Exception as e:
        print(f"DATABASE ERROR (add_favorite): {e}")
        return False


# -------------------------
# CREATE NOTE
# -------------------------

def add_note_db(code, note):
    """
    Generates a unique UUID and saves a new note record to DynamoDB.
    Args:
        code (str): The 3-letter country code.
        note (str): The text content provided by the user.
    """
    try:
        notes_table = dynamodb.Table('Notes')
        # Generating a unique ID for the Partition Key to prevent overwrites
        unique_id = str(uuid.uuid4())
        
        notes_table.put_item(
            Item={
                'id': unique_id,
                'country_code': code,
                'note': note
            }
        )
        return True
    except Exception as e:
        print(f"DATABASE ERROR (add_note_db): {e}")
        return False

# -------------------------
# READ NOTES
# -------------------------

def get_notes_db():
 
    try:
        # Initializing resource specifically to ensure region alignment
        db_resource = boto3.resource('dynamodb', region_name='us-east-1')
        table = db_resource.Table('Notes') 
        response = table.scan()
        return response.get('Items', [])
    except Exception as e:
        print(f"DATABASE ERROR (get_notes_db): {e}")
        return []


# -------------------------
# UPDATE NOTE
# -------------------------

def update_note_db(note_id, new_note_text):
    try:
        # Using update_item to only change the 'note' attribute without replacing the whole row
        notes_table.update_item(
            Key={'id': note_id},
            UpdateExpression="set note = :val",
            ExpressionAttributeValues={':val': new_note_text}
        )
        print(f"Successfully updated note {note_id}")
        return True
    except Exception as e:
        print(f"DATABASE ERROR (update_note_db): {e}")
        return False


# -------------------------
# DELETE NOTE
# -------------------------

def delete_note_db(note_id):
    """
    Permanently removes a note from the DynamoDB 'Notes' table.
    Ensures the ID is formatted as a string to match the Partition Key type.
    """
    try:
        # Typecasting to string for data integrity
        note_id_str = str(note_id) 
        
        notes_table.delete_item(
            Key={'id': note_id_str}
        )
        return True
    except Exception as e:
        print(f"DATABASE ERROR (delete_note_db): {e}")
        return False