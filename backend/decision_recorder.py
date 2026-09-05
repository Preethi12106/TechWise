from database import get_connection, create_table


def record_decision(
    decision,
    context,
    reason,
    alternatives,
    consequences
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO decisions
        (decision, context, reason, alternatives, consequences)
        VALUES (?, ?, ?, ?, ?)
    """, (
        decision,
        context,
        reason,
        alternatives,
        consequences
    ))

    connection.commit()

    decision_id = cursor.lastrowid

    connection.close()

    return decision_id


if __name__ == "__main__":

    create_table()

    decision = input("Enter the technology/decision: ")
    context = input("Enter the context: ")
    reason = input("Enter the reason: ")
    alternatives = input("Enter the alternatives: ")
    consequences = input("Enter the consequences: ")

    decision_id = record_decision(
        decision,
        context,
        reason,
        alternatives,
        consequences
    )

    print(f"\nDecision recorded successfully. ID: {decision_id}")