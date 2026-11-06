# InsureIQ – Project Details

## 1. Project Information

| Item | Details |
|---|---|
| Project title | InsureIQ – Insurance Claims Management System |
| Project category | Database Management System (DBMS) project |
| Application type | Web application |
| Backend | Python with Flask |
| Database | MongoDB |
| Database driver | PyMongo |

## 2. Project Description

InsureIQ is a web-based insurance claims management application developed using Python Flask and MongoDB. It provides a browser-based interface for managing insurance claim records. The application brings together claim registration, viewing, searching, filtering, updating, deletion, analytics, statistics, indexing, query-performance analysis, and natural-language search features.

The application uses the existing MongoDB database `insurance_company` and collection `insurance_data`.

## 3. Project Objectives

1. Develop a web-based system for managing insurance claim records.
2. Connect a Python Flask application to a MongoDB database.
3. Implement Create, Read, Update, and Delete (CRUD) operations.
4. Provide search and filtering facilities for claim records.
5. Generate analytical summaries and statistical information from claim data.
6. Demonstrate MongoDB indexing and query-performance analysis.
7. Provide a natural-language search interface for supported claim queries.

## 4. Technology Stack

| Layer / Purpose | Technology |
|---|---|
| Front end | HTML, CSS, JavaScript |
| Back end | Python, Flask |
| Database | MongoDB |
| Database connectivity | PyMongo |
| Environment configuration | python-dotenv |

## 5. Main Project Modules

### 5.1 Dashboard

Provides an overview of insurance claim records and selected summary metrics.

### 5.2 Claim Registration

Allows a user to enter policy, customer, incident, vehicle, and claim information and insert a new document into MongoDB. Required fields and policy-number duplication should be validated.

### 5.3 View and Search Claims

Displays claim records and allows users to search using fields supported by the application.

### 5.4 Claim Details

Displays the stored information for an individual claim.

### 5.5 Update Claim

Allows an existing claim to be edited. Existing values, especially dates, should remain unchanged when unrelated fields are edited.

### 5.6 Delete Claim

Allows a selected claim record to be deleted after confirmation.

### 5.7 Filter Claims

Provides filtering based on the criteria supported by the application.

### 5.8 Analytics

Provides summaries of claim data, such as claims grouped by incident type, incident state, fraud status, or vehicle information, depending on the implemented analytics.

### 5.9 Statistics

Calculates statistical summaries for claim amounts.

### 5.10 Index Management

Displays the indexes available on the MongoDB collection and provides index creation or verification functionality where the database user's permissions allow it.

### 5.11 Query Performance Analysis

Demonstrates the difference between a collection scan and an indexed query using MongoDB execution statistics. Metrics may include execution time, documents examined, keys examined, and returned documents.

### 5.12 AI Natural-Language Search

Interprets supported natural-language questions, converts them into database search criteria, and retrieves matching claim records. The exact range of supported questions depends on the application's query interpretation logic.

### 5.13 Months as Customer Calculation

In the updated application workflow, Months as Customer is intended to be calculated as the number of completed months between the Policy Bind Date and the current date. It represents customer tenure and is not an auto-incrementing record identifier.

## 6. Database Details

| Item | Value |
|---|---|
| Database | `insurance_company` |
| Collection | `insurance_data` |
| Database type | MongoDB document database |
| Connection variable | `MONGODB_URI` |

The application connects to the existing collection. The dataset contains policy, customer, incident, claim, vehicle, and fraud-related information.

**Data handling note:** In the existing dataset, numeric-looking fields are stored as strings. The application must account for this when performing numeric comparisons, sorting, or calculations. Policy-number searches should use the same string type as the stored values.

For additional collection and field information, see [`DATABASE_DETAILS.md`](DATABASE_DETAILS.md).

## 7. DBMS Concepts Demonstrated

- MongoDB database connectivity
- Document-based data storage
- CRUD operations
- Search queries and filtering
- Numeric conversion for calculations on numeric-looking string values
- Aggregation and statistical analysis
- Index creation and index inspection
- Query execution statistics and performance comparison

## 8. How to Run the Project

1. Extract the project folder.
2. Open the folder in a terminal or VS Code.
3. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment.

   **Windows PowerShell:**

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   **Windows Command Prompt:**

   ```cmd
   venv\Scripts\activate.bat
   ```

   **macOS/Linux:**

   ```bash
   source venv/bin/activate
   ```

5. Install the required packages:

   ```bash
   pip install flask pymongo python-dotenv
   ```

   If a `requirements.txt` file is provided, use:

   ```bash
   pip install -r requirements.txt
   ```

6. Create a `.env` file in the project root and configure the MongoDB connection:

   ```env
   MONGODB_URI=your_mongodb_connection_string
   FLASK_SECRET_KEY=your_secret_key
   ```

7. Ensure the MongoDB deployment is accessible and the database user has the required permissions.
8. Start the application:

   ```bash
   python app.py
   ```

9. Open the local URL displayed in the terminal in a web browser.

## 9. Important Notes

- Do not include `.env` or database credentials when sharing the project.
- The application uses the existing `insurance_company.insurance_data` collection.
- Back up important data before testing update and delete operations.
- Use test records when demonstrating destructive operations.
- Confirm that the live collection's field names and data types match the application's assumptions.
- Creating indexes requires suitable MongoDB permissions.
- Query-performance measurements can vary with server load, network latency, data volume, and index state.
- Verify all modules in the final running version before project submission.

## 10. Conclusion

InsureIQ demonstrates how a web application can be connected to MongoDB to manage insurance claim records. It combines CRUD operations with search, filtering, analytics, statistics, indexing, and query-performance analysis to demonstrate practical database management concepts.
