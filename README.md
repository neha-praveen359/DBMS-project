# InsureIQ – Insurance Claims Management System

InsureIQ is a Flask-based web application for managing insurance claim records stored in MongoDB. It provides a browser-based interface for registering, viewing, searching, filtering, updating, and deleting claims, along with analytics, statistics, indexing demonstrations, and natural-language search.

## Features

- **Dashboard:** Displays an overview of claim records and key claim metrics.
- **Register Claim:** Adds a new insurance claim to the MongoDB collection.
- **View and Search Claims:** Displays claim records and supports searches using available claim fields.
- **Claim Details:** Shows the information stored for an individual claim.
- **Update Claim:** Edits an existing claim.
- **Delete Claim:** Deletes a selected claim after confirmation.
- **Filter Claims:** Filters records using supported field and range criteria.
- **Analytics:** Summarizes claims by incident type, incident state, fraud status, and vehicle details.
- **Statistics:** Presents statistical summaries of claim amounts.
- **Index Management:** Displays MongoDB indexes and provides an option to create or verify the indexes used by the application.
- **Query Performance:** Compares a collection scan with an indexed policy-number search using MongoDB execution statistics.
- **AI Natural-Language Search:** Converts supported natural-language questions into database search criteria and displays matching claims.
- **Months as Customer:** The updated registration/edit workflow calculates the number of completed months from the policy bind date to the current date. Check the running version of the application to confirm this behaviour.

## Technology Stack

- Python
- Flask
- MongoDB
- MongoDB PyMongo driver
- HTML and CSS
- JavaScript
- python-dotenv

## Project Structure

```text
Project/
├── app.py                  # Flask application, routes, MongoDB operations
├── AI.py                   # Natural-language query interpretation and search
├── analytics.py            # Claim analytics functions
├── statistics.py           # Claim amount statistics
├── indexing.py             # Index creation/listing and query-performance helpers
├── templates/              # HTML templates used by Flask
│   ├── base.html
│   ├── dashboard.html
│   ├── analytics.html
│   ├── statistics.html
│   ├── ai_search.html
│   ├── indexes.html
│   ├── performance.html
│   └── claims/
│       ├── form.html
│       ├── search.html
│       ├── detail.html
│       └── filter.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## Requirements

- Python 3.9 or later is recommended.
- A MongoDB deployment, such as MongoDB Atlas, with network access enabled for the application.
- A MongoDB connection string and database permissions appropriate for the operations being used.

## Setup and Installation

### 1. Extract the project

Extract the project ZIP and open the extracted project folder in a terminal or VS Code.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows PowerShell**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install flask pymongo python-dotenv
```

If your project includes a `requirements.txt`, you can instead install the listed dependencies with:

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB

Create a file named `.env` in the same folder as `app.py`:

```env
MONGODB_URI=your_mongodb_connection_string
FLASK_SECRET_KEY=replace_with_a_long_random_secret
```

Replace the placeholder with your own MongoDB connection string. Do not commit or share the `.env` file. Do not paste database credentials into source code.

The application is configured to use:

- Database: `insurance_company`
- Collection: `insurance_data`

Make sure the MongoDB user has the permissions required for the features you intend to use. In particular, creating indexes requires suitable database privileges.

### 5. Run the application

```bash
python app.py
```

Open the local address printed in the terminal (commonly `http://127.0.0.1:5000`) in a web browser.

## Database Notes

- The application connects to the existing `insurance_company.insurance_data` collection.
- Keep a backup of important data before testing update or delete operations.
- Policy numbers in the supplied dataset are stored as strings; search using the same string representation.
- Numeric-looking values in the original dataset may also be stored as strings. The application must convert values when performing numeric calculations or range comparisons.
- Do not re-import the dataset into the live collection unless you intentionally want to replace or duplicate records.
- The application checks policy-number uniqueness when registering or changing a policy number. The exact uniqueness rule should be confirmed against your team's requirements.

## Testing Checklist

Before a project demonstration, verify the following:

1. The dashboard loads and displays database information.
2. A new claim can be registered.
3. Existing claims can be viewed and searched.
4. An existing claim can be edited and the changes persist after refresh.
5. Dates remain populated when editing unrelated fields.
6. A claim can be deleted after confirmation (use a test record).
7. Filters return the expected records.
8. Analytics and statistics pages load.
9. The index page displays the indexes available in MongoDB.
10. Query-performance results show execution statistics for both scan types.
11. Natural-language searches return sensible results for supported queries.
12. Months as Customer is calculated according to the policy bind date and current date in the version being demonstrated.

## Security and Good Practices

- Keep `.env` out of version control. Add `.env` to `.gitignore`.
- Never publish your MongoDB URI, database password, or Flask secret key.
- Use a strong `FLASK_SECRET_KEY` outside local development.
- Restrict MongoDB network access and database permissions.
- Confirm destructive actions before deleting records.
- Test changes using sample records before modifying important data.

## Limitations

Natural-language search depends on the query patterns and fields supported by the application's query parser; it should not be assumed to understand every possible sentence. Query execution times can vary with database size, network latency, server load, and index state. A single execution-statistics comparison is a demonstration, not a comprehensive benchmark.

## Project Purpose

This project demonstrates the application of DBMS concepts through a practical insurance claims management application, including CRUD operations, querying and filtering, aggregation/analytics, indexing, and query-performance analysis.
