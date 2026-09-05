from database import get_connection, create_table


def retrieve_decisions(keyword):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, decision, context, reason, alternatives, consequences, created_at
        FROM decisions
        WHERE decision LIKE ?
           OR context LIKE ?
           OR reason LIKE ?
           OR alternatives LIKE ?
           OR consequences LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    results = cursor.fetchall()

    connection.close()

    return results


if __name__ == "__main__":

    create_table()

    keyword = input("What decision do you want to search for? ")

    results = retrieve_decisions(keyword)

    if results:
        print("\nMatching decisions:\n")

        for result in results:
            print("ID:", result[0])
            print("Decision:", result[1])
            print("Context:", result[2])
            print("Reason:", result[3])
            print("Alternatives:", result[4])
            print("Consequences:", result[5])
            print("Created At:", result[6])
            print("-" * 50)

    else:
        print("No matching decisions found.")