# [World Explorer ]

**CS178: Cloud and Database Systems — Project #1**
**Author:** [Colton Ferguson]
**GitHub:** [https://github.com/cferg9/cs178-flask-app.git]

---

## Overview

I really enjoy geography and wanted to use the pre-exisiting "world" database that was provided to us to use
in class. I decided to make a little World Explorer where you can add your favorite countries, make notes about your 
favorite countries, which allows you to update those notes, and also delete them if you don't want them anymore. This database reads from a list of 20 countries to experiment with that are composed of important information about each country. This includes the capital, population, and other info. 

---

## Technologies Used

- **Flask** — Python web framework
- **AWS EC2** — hosts the running Flask application
- **AWS RDS (MySQL)** — relational database for [describe what you stored]
- **AWS DynamoDB** — non-relational database for [describe what you stored]
- **GitHub Actions** — auto-deploys code from GitHub to EC2 on push

---

## Project Structure

```
ProjectOne/
├── flaskapp.py          # Main Flask application — routes and app logic
├── dbCode.py            # Database helper functions (MySQL connection + queries)
├── creds_sample.py      # Sample credentials file (see Credential Setup below)
├── templates/
│   ├── home.html        # Landing page
│   ├── [other].html     # Add descriptions for your other templates
├── .gitignore           # Excludes creds.py and other sensitive files
└── README.md
```

---

## How to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Install dependencies:

   ```bash
   pip3 install flask pymysql boto3
   ```

3. Set up your credentials (see Credential Setup below)

4. Run the app:

   ```bash
   python3 flaskapp.py
   ```

5. Open your browser and go to `http://127.0.0.1:8080`

---

## How to Access in the Cloud

The app is deployed on an AWS EC2 instance. To view the live version:

```
http://[your-ec2-public-ip]:8080
```

_(Note: the EC2 instance may not be running after project submission.)_

---

## Credential Setup

This project requires a `creds.py` file that is **not included in this repository** for security reasons.

Create a file called `creds.py` in the project root with the following format (see `creds_sample.py` for reference):

```python
# creds.py — do not commit this file
host = "your-rds-endpoint"
user = "admin"
password = "your-password"
db = "your-database-name"
```

---

## Database Design

### SQL (MySQL on RDS)

<!-- Briefly describe your relational database schema. What tables do you have? What are the key relationships? -->
Inside the "world" database, the main table is "Country" with columns named code(Primary Key) , name, continent, and population. The "Code" column is the key relationship that all other columns depend on as no other country can have the same country code. This ensures all countries are unique. 

- `[Country]` — stores global geographic, demographic, and economic statistics for 197 nations; primary key is the 3-letter ISO; `[Code]`
- `[Capital]` — stores the specific city ID assigned as the seat of government; foreign key links to the ID column in the `[city table]`. 
- `[Language]` — stores the names, official status, and speaker percentages for various regions; foreign key links to the `[CountryCode]` in the country table.

The JOIN query used in this project: 

The JOIN query is located in the country_detail route within flaskapp.py. This route is triggered whenever a user clicks "View" on a specific country from your main list. This query performs a LEFT JOIN between the country table and the city table. It matches the Capital column (which contains an ID number) from the country record to the ID column in the city table.


### DynamoDB

<!-- Describe your DynamoDB table. What is the partition key? What attributes does each item have? How does it connect to the rest of the app? -->

My project utilizes two DynamoDB tables to manage user interaction: the notes table, which uses a unique UUID partition key to store text entries linked to nations via a country\_code, and the favorites table, which uses a composite key (User and Country) to track saved locations. These tables connect with Flask by allowing the app to query specific user data, like personalized notes or favorite statuses, based on the country currently being viewed.

- **Table name:** `[Notes`
- **Partition key:** `[id]`
- **Used for:** [Adding your own notes about any of the 197 countries, can be updated, created, deleted and read from the DynamoDB database.]

- **Table name:** `[Favorites]`
- **Partition key:** `[User]`
- **Used for:** [Adding your favorite countries to the 'favorites' tab in the World Explorer, to keep track of your
favorite countries.]

---

## CRUD Operations

| Operation | Route         | Description    |
| --------- | -----------   | -------------- |
| Create    | `add_note`    | [allows you to add notes to the note tab] |
| Read      | `countries`   | [displays all countries and favorites]    |
| Update    | `update_note` | [Updates whichever note you choose]       |
| Delete    | `delete_note` | [Deletes whichever not you choose]        |

---

## Challenges and Insights

<!-- What was the hardest part? What did you learn? Any interesting design decisions? -->
The hardest part about this project was getting everythig linked, I ran into a bunch of connection errors with mySQL
not wanting to work and learing that all that was wrong was the endpoint I had copied and pasted in was slightly different than what I needed to have. Then I couldn't get my Notes and Favorites tabs to work when I soon realized I needed to create the actual tables on AWS first. So luckily, nothing actual ever broke, it was just very minimal errors that were hard to find in the volume of code that I have. 
---

## AI Assistance

I utilized Gemini for debugging all the problems listed above, it gave me the try/catch statements to ensure things would run. I tried asking ChatGPT for help with debugging but it had no idea what to do, so I went to gemini instead. 
