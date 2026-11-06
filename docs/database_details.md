# Database Details – InsureIQ

## 1. Database Overview

InsureIQ uses MongoDB as its database. The application stores insurance policy and claim information as MongoDB documents in a collection.

| Item | Value |
|---|---|
| Database name | `insurance_company` |
| Collection name | `insurance_data` |
| Database type | NoSQL, document-oriented database |
| Python database driver | PyMongo |
| Connection configuration | `MONGODB_URI` environment variable in `.env` |

The application is intended to connect to the existing MongoDB database and collection. It does not need to recreate or re-upload the dataset each time the application starts.

## 2. Connection Configuration

The MongoDB connection string is stored in a local `.env` file. Example:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-address>/
FLASK_SECRET_KEY=<your-secret-key>
```

Replace the placeholders with the values for your own MongoDB deployment. Do not commit the `.env` file to Git or include it when sharing the project. Never publish the MongoDB username, password, connection string, or Flask secret key.

The MongoDB deployment must allow network access from the machine running the application. The database user must have the permissions required for the operations being used.

## 3. Collection and Document Structure

The `insurance_data` collection contains insurance claim records. Each record is stored as a MongoDB document and has a unique MongoDB `_id` field.

The dataset used by the project contains fields relating to:

- Customer and policy information
- Incident information
- Claim amounts
- Vehicle information
- Fraud reporting

The source dataset's field names are retained in the collection. Some field names use underscores, and some names may contain hyphens. Use the exact field names present in MongoDB when writing queries.

### Common fields in the insurance claim dataset

The following are fields used by the dataset/project. Confirm the exact field list against the live collection before relying on it as a complete schema.

| Field | Description |
|---|---|
| `_id` | MongoDB-generated unique document identifier |
| `months_as_customer` | Number of completed months the customer has been with the insurer |
| `age` | Insured person's age |
| `policy_number` | Insurance policy number |
| `policy_bind_date` | Date the policy was bound |
| `policy_state` | State associated with the policy |
| `policy_csl` | Combined single-limit policy coverage |
| `policy_deductable` | Policy deductible (source field spelling retained) |
| `policy_annual_premium` | Annual policy premium |
| `umbrella_limit` | Umbrella coverage limit |
| `insured_zip` | Insured person's ZIP/postal code |
| `insured_sex` | Insured person's sex value as recorded in the dataset |
| `insured_education_level` | Insured person's education level |
| `insured_occupation` | Insured person's occupation |
| `insured_hobbies` | Insured person's hobbies |
| `insured_relationship` | Insured person's relationship status/relationship field |
| `capital-gains` | Capital gains value |
| `capital-loss` | Capital loss value |
| `incident_date` | Date of the incident |
| `incident_type` | Type of incident |
| `collision_type` | Type of collision, where applicable |
| `incident_severity` | Recorded incident severity |
| `authorities_contacted` | Authority contacted in relation to the incident |
| `incident_state` | State where the incident occurred |
| `incident_city` | City where the incident occurred |
| `incident_location` | Incident location |
| `incident_hour_of_the_day` | Hour of the day when the incident occurred |
| `number_of_vehicles_involved` | Number of vehicles involved |
| `property_damage` | Property damage indicator |
| `bodily_injuries` | Number of bodily injuries |
| `witnesses` | Number of witnesses |
| `police_report_available` | Indicates whether a police report is available |
| `total_claim_amount` | Total claim amount |
| `injury_claim` | Injury-related claim amount |
| `property_claim` | Property-related claim amount |
| `vehicle_claim` | Vehicle-related claim amount |
| `auto_make` | Vehicle manufacturer |
| `auto_model` | Vehicle model |
| `auto_year` | Vehicle year |
| `fraud_reported` | Fraud indicator as recorded in the dataset |

**Schema note:** This table describes the commonly used fields in the insurance claims dataset. It is not a MongoDB-enforced schema declaration. The collection may contain additional fields or may differ in field availability. The live collection is the source of truth.

## 4. Data Types and Important Handling Notes

In the existing project collection, the imported dataset's values are stored as strings for the fields, except for MongoDB's `_id` field. Therefore, values that look numeric (for example, `age`, `months_as_customer`, `total_claim_amount`, and `policy_annual_premium`) may still be stored as strings.

This affects database operations:

- Equality searches should use the same data type as the stored value. For example, search for a policy number using `"842643"` rather than integer `842643`.
- Numeric range filters should convert string values to numbers before comparing them, either in application code or through a suitable MongoDB aggregation expression.
- Sorting numeric-looking strings directly in MongoDB can produce string ordering rather than numeric ordering.
- Date strings should be parsed using the format actually stored in the collection before date calculations or comparisons.
- Preserve the original field names, including spellings such as `policy_deductable`, when accessing the existing collection.

Do not change the existing collection's data types or re-import the dataset unless the project team has explicitly decided to migrate the data.

## 5. Main Database Operations

The application uses the collection for the following operations:

| Operation | Purpose |
|---|---|
| Insert | Register a new insurance claim |
| Find | Display claim records and retrieve a claim by its identifier or policy number |
| Update | Modify fields in an existing claim |
| Delete | Remove a selected claim after user confirmation |
| Filter | Retrieve claims matching selected criteria |
| Aggregate | Produce grouped summaries and analytical results |
| Index inspection | Display indexes defined on the collection |
| Explain query | Inspect query execution statistics for performance demonstration |

For update and delete operations, the application should identify the intended document precisely. Before testing delete functionality, use a test record or take a database backup.

## 6. Indexes

Indexes can improve the performance of queries that search or sort on indexed fields. The project includes indexing and query-performance functionality.

The application may use indexes such as:

- `policy_number`
- `incident_state`
- `fraud_reported`

The actual indexes present in the database must be checked using MongoDB's index listing functionality. The names above describe indexes used or proposed by the project; they do not guarantee that each index currently exists in the live collection.

Creating an index requires appropriate MongoDB permissions. If the database user is not permitted to create indexes, an authorized administrator can create them in MongoDB Atlas or through an approved setup script. The web application can still display existing indexes and run performance demonstrations where permitted.

## 7. Query Performance Demonstration

The project demonstrates the difference between:

- A collection scan, which examines documents in the collection.
- An indexed query, which can use an index matching the query.

MongoDB `explain` execution statistics may include:

- `executionTimeMillis`
- `totalDocsExamined`
- `totalKeysExamined`
- `nReturned`

Execution time can vary due to network latency, server load, cache state, dataset size, and index state. A single comparison is a classroom demonstration and should not be treated as a controlled benchmark.

## 8. Months as Customer Calculation

In the updated application workflow, `months_as_customer` is intended to be calculated as the number of completed months between `policy_bind_date` and the current date.

This value represents customer tenure; it is not an auto-incrementing record ID. It should not be increased by one whenever a claim is inserted. The calculation should use the policy bind date and current date, and should reject invalid future bind dates.

Existing database documents are not necessarily recalculated in bulk. Verify the value saved for a new or edited claim in the running application.

## 9. Backup, Privacy, and Maintenance

- Back up the database before bulk updates, migrations, or destructive testing.
- Do not store credentials directly in Python source files.
- Keep `.env` out of version control.
- Grant the application only the database permissions it needs.
- Avoid exposing insured-person information unnecessarily in screenshots, logs, or project demonstrations.
- Use test records when demonstrating update and delete operations.
- Do not upload duplicate copies of the dataset into the live collection.

## 10. Verifying the Live Database

Before submission or demonstration, verify:

1. The application connects to `insurance_company`.
2. The application uses the `insurance_data` collection.
3. The expected claim documents are present.
4. Field names and stored data types match the assumptions in the application.
5. Policy-number searches use the correct string type.
6. Numeric filters and calculations correctly handle numeric strings.
7. Existing dates display correctly in edit forms and remain unchanged when unrelated fields are edited.
8. The displayed indexes match the indexes actually present in MongoDB.
9. Query-performance demonstrations run successfully with the database user's permissions.

---

**Important:** This document describes the database configuration and handling assumptions provided for the InsureIQ project. Always verify the live MongoDB collection before treating the field list, data types, or indexes as definitive.
