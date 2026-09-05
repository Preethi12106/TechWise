from database import get_connection, create_table


def get_decision(decision_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, decision, context, reason, alternatives, consequences
        FROM decisions
        WHERE id = ?
    """, (decision_id,))

    result = cursor.fetchone()

    connection.close()

    return result


def analyze_impact(decision_id, new_requirement):

    decision = get_decision(decision_id)

    if decision is None:
        return None

    decision_id, technology, context, reason, alternatives, consequences = decision

    return {
        "decision_id": decision_id,
        "original_decision": technology,
        "context": context,
        "original_reason": reason,
        "alternatives": alternatives,
        "consequences": consequences,
        "new_requirement": new_requirement
    }


if __name__ == "__main__":

    create_table()

    decision_id = int(input("Enter decision ID: "))

    new_requirement = input(
        "Enter the new project requirement: "
    )

    result = analyze_impact(
        decision_id,
        new_requirement
    )

    print("\nDecision Impact Analysis")
    print("-" * 40)

    if result is None:

        print("Decision not found.")

    else:

        print("Decision ID:", result["decision_id"])
        print("Original Decision:", result["original_decision"])
        print("Context:", result["context"])
        print("Original Reason:", result["original_reason"])
        print("Alternatives:", result["alternatives"])
        print("Consequences:", result["consequences"])
        print("New Requirement:", result["new_requirement"])