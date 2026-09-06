from database import get_connection, create_table


def retrieve_decisions(keyword):

    if not keyword or not keyword.strip():
        return []

    connection = get_connection()
    cursor = connection.cursor()

    words = keyword.split()

    conditions = []
    values = []

    for word in words:

        conditions.append("""
            (
                decision LIKE ?
                OR context LIKE ?
                OR reason LIKE ?
                OR alternatives LIKE ?
                OR consequences LIKE ?
            )
        """)

        pattern = f"%{word}%"

        values.extend([
            pattern,
            pattern,
            pattern,
            pattern,
            pattern
        ])

    query = f"""
        SELECT id, decision, context, reason, alternatives, consequences, created_at
        FROM decisions
        WHERE {" OR ".join(conditions)}
        ORDER BY id DESC
    """

    cursor.execute(query, values)

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