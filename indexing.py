from pymongo import ASCENDING


# ============================================================
# 1. CREATE INDEXES
# ============================================================

def create_indexes(collection):
    """
    Create indexes for fields that are frequently searched.

    policy_number:
        Frequently used to locate one specific claim.

    incident_state:
        Frequently used for filtering claims by state.

    fraud_reported:
        Frequently used for fraud/non-fraud analysis.
    """

    print("\n" + "=" * 60)
    print("                 CREATE DATABASE INDEXES")
    print("=" * 60)

    try:
        policy_index = collection.create_index(
            [("policy_number", ASCENDING)],
            name="idx_policy_number"
        )

        state_index = collection.create_index(
            [("incident_state", ASCENDING)],
            name="idx_incident_state"
        )

        fraud_index = collection.create_index(
            [("fraud_reported", ASCENDING)],
            name="idx_fraud_reported"
        )

        print("\nIndexes created/verified successfully.")
        print("1. policy_number    ->", policy_index)
        print("2. incident_state   ->", state_index)
        print("3. fraud_reported   ->", fraud_index)

    except Exception as error:
        print("\nUnable to create indexes.")
        print("Error:", error)


# ============================================================
# 2. DISPLAY CURRENT INDEXES
# ============================================================

def show_indexes(collection):
    """Display all indexes currently present on the collection."""

    print("\n" + "=" * 60)
    print("                    CURRENT INDEXES")
    print("=" * 60)

    try:
        indexes = list(collection.list_indexes())

        for index in indexes:
            print("\nIndex name:", index.get("name"))
            print("Key:", index.get("key"))

        print("\nTotal indexes:", len(indexes))

    except Exception as error:
        print("\nUnable to display indexes.")
        print("Error:", error)


# ============================================================
# 3. EXPLAIN QUERY PERFORMANCE
# ============================================================

def _get_execution_stats(explain_result):
    """
    Extract execution statistics from an explain() result.

    MongoDB normally returns:
        executionStats.executionTimeMillis
        executionStats.totalDocsExamined
        executionStats.totalKeysExamined
    """

    stats = explain_result.get("executionStats", {})

    return {
        "execution_time_ms": stats.get("executionTimeMillis"),
        "documents_examined": stats.get("totalDocsExamined"),
        "keys_examined": stats.get("totalKeysExamined"),
        "n_returned": stats.get("nReturned")
    }


def demonstrate_query_performance(collection):
    """
    Compare a collection scan with an indexed query.

    The comparison uses policy_number because it is the most
    natural exact-search field in the application.

    A real policy number is requested from the user. If the
    number does not exist, the demonstration still shows the
    query plans and examined documents/keys.
    """

    print("\n" + "=" * 60)
    print("             QUERY PERFORMANCE DEMONSTRATION")
    print("=" * 60)

    policy_number = input(
        "\nEnter a Policy Number for the performance test: "
    ).strip()

    if policy_number == "":
        print("Policy number cannot be empty.")
        return

    try:
        # ------------------------------------------------------
        # Make sure the required index exists.
        # ------------------------------------------------------
        collection.create_index(
            [("policy_number", ASCENDING)],
            name="idx_policy_number"
        )

        query = {"policy_number": policy_number}

        # ------------------------------------------------------
        # A. Collection scan (without using the index)
        # ------------------------------------------------------
        # Use MongoDB's explain command directly. This avoids
        # Cursor.explain() compatibility issues between PyMongo
        # versions.
        collection_scan_explain = collection.database.command(
            "explain",
            {
                "find": collection.name,
                "filter": query,
                "hint": {"$natural": 1}
            },
            verbosity="executionStats"
        )

        collection_scan_stats = _get_execution_stats(
            collection_scan_explain
        )

        # ------------------------------------------------------
        # B. Indexed query
        # ------------------------------------------------------
        indexed_explain = collection.database.command(
            "explain",
            {
                "find": collection.name,
                "filter": query,
                "hint": "idx_policy_number"
            },
            verbosity="executionStats"
        )

        indexed_stats = _get_execution_stats(
            indexed_explain
        )

        # ------------------------------------------------------
        # Display comparison
        # ------------------------------------------------------
        print("\n" + "-" * 60)
        print("WITHOUT INDEX (COLLECTION SCAN)")
        print("-" * 60)

        print(
            "Execution time:",
            collection_scan_stats["execution_time_ms"],
            "ms"
        )
        print(
            "Documents examined:",
            collection_scan_stats["documents_examined"]
        )
        print(
            "Index keys examined:",
            collection_scan_stats["keys_examined"]
        )
        print(
            "Documents returned:",
            collection_scan_stats["n_returned"]
        )

        print("\n" + "-" * 60)
        print("WITH INDEX (policy_number)")
        print("-" * 60)

        print(
            "Execution time:",
            indexed_stats["execution_time_ms"],
            "ms"
        )
        print(
            "Documents examined:",
            indexed_stats["documents_examined"]
        )
        print(
            "Index keys examined:",
            indexed_stats["keys_examined"]
        )
        print(
            "Documents returned:",
            indexed_stats["n_returned"]
        )

        print("\n" + "=" * 60)
        print("                 PERFORMANCE ANALYSIS")
        print("=" * 60)

        collection_docs = collection_scan_stats["documents_examined"]
        indexed_docs = indexed_stats["documents_examined"]

        collection_keys = collection_scan_stats["keys_examined"]
        indexed_keys = indexed_stats["keys_examined"]

        print(
            "\nCollection scan examined",
            collection_docs,
            "document(s)."
        )

        print(
            "Indexed query examined",
            indexed_docs,
            "document(s)."
        )

        print(
            "\nCollection scan examined",
            collection_keys,
            "index key(s)."
        )

        print(
            "Indexed query examined",
            indexed_keys,
            "index key(s)."
        )

        if (
            collection_docs is not None
            and indexed_docs is not None
            and collection_docs > indexed_docs
        ):
            print(
                "\nResult: The index reduced the number of "
                "documents that MongoDB needed to examine."
            )
        else:
            print(
                "\nNote: With a small dataset, the execution time "
                "difference may be very small. The number of "
                "documents/keys examined is still useful for "
                "demonstrating index usage."
            )

        print(
            "\nFor the project presentation, explain that an index "
            "allows MongoDB to locate matching values more directly "
            "instead of scanning every document."
        )

    except Exception as error:
        print("\nUnable to run the performance demonstration.")
        print("Error:", error)


# ============================================================
# 4. PERSON 3 MENU
# ============================================================

def indexing_menu(collection):
    """
    Menu for Person 3's indexing functionality.

    This menu can be called from the main app.py menu.
    """

    while True:
        print("\n" + "=" * 60)
        print("             INDEXING & PERFORMANCE")
        print("=" * 60)

        print("1. Create/Verify Indexes")
        print("2. Show Current Indexes")
        print("3. Demonstrate Query Performance")
        print("4. Back to Main Menu")

        print("=" * 60)

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            create_indexes(collection)

        elif choice == "2":
            show_indexes(collection)

        elif choice == "3":
            demonstrate_query_performance(collection)

        elif choice == "4":
            break

        else:
            print("\nInvalid choice. Enter a number from 1 to 4.")
