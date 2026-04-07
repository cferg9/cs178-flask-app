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
    """Returns all items from the Favorites DynamoDB table."""
    try:
        response = favorites_table.scan()
        return response.get('Items', [])
    except Exception as e:
        print("Error fetching favorites:", e)
        return []

def add_favorite(user, country_code):
    favorites_table = dynamodb.Table('Favorites')
    favorites_table.put_item(
        Item={
            'User': user,          # Matches the Partition Key
            'Country': country_code # Matches the Sort Key
        }
    )


# -------------------------
# CREATE NOTE
# -------------------------
def add_note_db(code, note):
    import uuid
    notes_table = dynamodb.Table('Notes')
    notes_table.put_item(
        Item={
            'id': str(uuid.uuid4()), # Matches the Partition Key
            'country_code': code,
            'note': note
        }
    )

# -------------------------
# READ NOTES
# -------------------------
def get_notes_db():

    try:
        test_db = boto3.resource('dynamodb', region_name='us-east-1')
        test_table = test_db.Table('Notes') 
        response = test_table.scan()
        return response.get('Items', [])
    except Exception as e:
    
        print(f"DEBUG ERROR: {e}")
        return []


# -------------------------
# UPDATE NOTE
# -------------------------
def update_note_db(note_id, new_note_text):
    try:
        # Ensure the key name 'id' is lowercase to match your AWS table
        notes_table.update_item(
            Key={
                'id': note_id 
            },
            # 'set note = :val' tells AWS: "Change the 'note' column to this new value"
            UpdateExpression="set note = :val",
            ExpressionAttributeValues={
                ':val': new_note_text
            }
        )
        print(f"Successfully updated note {note_id}")
        return True
    except Exception as e:
        print(f"UPDATE ERROR: {e}")
        return False


# -------------------------
# DELETE NOTE
# -------------------------
def delete_note_db(note_id):
    try:
    
        note_id_str = str(note_id) 
        
        notes_table.delete_item(
            Key={
                'id': note_id_str 
            }
        )
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False