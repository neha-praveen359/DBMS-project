from pymongo.errors import PyMongoError


# ============================================================
# 1. CLAIM AMOUNT STATISTICS
# ============================================================

def claim_amount_statistics(collection, display=True):

    print("\n" + "=" * 60)
    print("                 CLAIM AMOUNT STATISTICS")
    print("=" * 60)

    pipeline = [
        {
            "$group": {
                "_id": None,
                "claim_count": {"$sum": 1},
                "total_claim_amount": {
                    "$sum": {
                        "$convert": {
                            "input": "$total_claim_amount",
                            "to": "double",
                            "onError": 0,
                            "onNull": 0
                        }
                    }
                },
                "average_claim_amount": {
                    "$avg": {
                        "$convert": {
                            "input": "$total_claim_amount",
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    }
                },
                "maximum_claim_amount": {
                    "$max": {
                        "$convert": {
                            "input": "$total_claim_amount",
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    }
                },
                "minimum_claim_amount": {
                    "$min": {
                        "$convert": {
                            "input": "$total_claim_amount",
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    }
                },
                "claim_amount_standard_deviation": {
                    "$stdDevPop": {
                        "$convert": {
                            "input": "$total_claim_amount",
                            "to": "double",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "claim_count": 1,
                "total_claim_amount": {
                    "$round": ["$total_claim_amount", 2]
                },
                "average_claim_amount": {
                    "$round": ["$average_claim_amount", 2]
                },
                "maximum_claim_amount": {
                    "$round": ["$maximum_claim_amount", 2]
                },
                "minimum_claim_amount": {
                    "$round": ["$minimum_claim_amount", 2]
                },
                "claim_amount_range": {
                    "$round": [
                        {
                            "$subtract": [
                                "$maximum_claim_amount",
                                "$minimum_claim_amount"
                            ]
                        },
                        2
                    ]
                },
                "claim_amount_standard_deviation": {
                    "$round": [
                        "$claim_amount_standard_deviation",
                        2
                    ]
                }
            }
        }
    ]

    try:
        results = list(collection.aggregate(pipeline))

        if not results:
            print("\nNo claim data found.")
            return

        result = results[0]

        print("\n" + "-" * 60)
        print("CLAIM AMOUNT SUMMARY")
        print("-" * 60)

        print("Number of claims              :", result.get("claim_count"))
        print("Total claim amount            :", result.get("total_claim_amount"))
        print("Average claim amount         :", result.get("average_claim_amount"))
        print("Maximum claim amount         :", result.get("maximum_claim_amount"))
        print("Minimum claim amount         :", result.get("minimum_claim_amount"))
        print("Claim amount range           :", result.get("claim_amount_range"))
        print(
            "Standard deviation           :",
            result.get("claim_amount_standard_deviation")
        )

        print("\n" + "=" * 60)

    except PyMongoError as error:
        print("\nUnable to calculate claim amount statistics.")
        print("Error:", error)


# ============================================================
# 2. CLAIM AMOUNT MENU
# ============================================================

def claim_amount_menu(collection):

    while True:
        print("\n" + "=" * 60)
        print("             CLAIM AMOUNT ANALYSIS")
        print("=" * 60)

        print("1. Display Claim Amount Statistics")
        print("0. Back to Main Menu")

        print("=" * 60)

        choice = input("Enter your choice (0-1): ").strip()

        if choice == "1":
            claim_amount_statistics(collection)

        elif choice == "0":
            break

        else:
            print("\nInvalid choice. Enter 0 or 1.")
