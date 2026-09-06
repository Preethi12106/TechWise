import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from decision_recorder import record_decision
from decision_retriever import retrieve_decisions
from decision_impact_analyzer import analyze_impact


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.6-flash"


# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

def record_decision_tool(
    decision,
    context,
    reason,
    alternatives,
    consequences
):
    """
    Store a software engineering decision in SQLite.
    """

    decision_id = record_decision(
        decision,
        context,
        reason,
        alternatives,
        consequences
    )

    return {
        "success": True,
        "decision_id": decision_id,
        "message": "Decision recorded successfully."
    }


def retrieve_decisions_tool(keyword):
    """
    Search stored decisions using keywords.
    """

    results = retrieve_decisions(keyword)

    formatted_results = []

    for result in results:
        formatted_results.append({
            "id": result[0],
            "decision": result[1],
            "context": result[2],
            "reason": result[3],
            "alternatives": result[4],
            "consequences": result[5],
            "created_at": result[6]
        })

    return formatted_results


def analyze_impact_tool(
    decision_id,
    new_requirement
):
    """
    Retrieve a stored decision and prepare its information
    for impact analysis.
    """

    result = analyze_impact(
        decision_id,
        new_requirement
    )

    if result is None:
        return {
            "success": False,
            "message": "Decision not found."
        }

    return result


# ============================================================
# GEMINI FUNCTION DECLARATIONS
# ============================================================

record_decision_function = {
    "type": "function",
    "name": "record_decision",
    "description": (
        "Record a software engineering decision in persistent "
        "SQLite memory. Use this only when the user explicitly "
        "asks to save or record a decision."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "decision": {
                "type": "string",
                "description": "The technology or engineering decision."
            },
            "context": {
                "type": "string",
                "description": "The project context."
            },
            "reason": {
                "type": "string",
                "description": "Why the team selected this decision."
            },
            "alternatives": {
                "type": "string",
                "description": "Alternatives that were considered."
            },
            "consequences": {
                "type": "string",
                "description": "Expected consequences."
            }
        },
        "required": [
            "decision",
            "context",
            "reason",
            "alternatives",
            "consequences"
        ]
    }
}


retrieve_decisions_function = {
    "type": "function",
    "name": "retrieve_decisions",
    "description": (
        "Search persistent memory for previous software "
        "engineering decisions. Use this when the user asks "
        "about an existing decision."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": (
                    "Keywords describing the technology, "
                    "project, or decision."
                )
            }
        },
        "required": [
            "keyword"
        ]
    }
}


analyze_impact_function = {
    "type": "function",
    "name": "analyze_impact",
    "description": (
        "Retrieve a previous software engineering decision "
        "and compare it with a new project requirement."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "decision_id": {
                "type": "integer",
                "description": "ID of the stored decision."
            },
            "new_requirement": {
                "type": "string",
                "description": (
                    "New project requirement that may affect "
                    "the previous decision."
                )
            }
        },
        "required": [
            "decision_id",
            "new_requirement"
        ]
    }
}


# ============================================================
# AVAILABLE TOOLS
# ============================================================

# Three custom TechWise tools + Gemini's built-in Google Search
tools = [
    {
        "type": "google_search"
    },
    record_decision_function,
    retrieve_decisions_function,
    analyze_impact_function
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(name, arguments):

    if name == "record_decision":

        return record_decision_tool(
            **arguments
        )

    elif name == "retrieve_decisions":

        return retrieve_decisions_tool(
            **arguments
        )

    elif name == "analyze_impact":

        return analyze_impact_tool(
            **arguments
        )

    else:

        return {
            "error": f"Unknown custom tool: {name}"
        }


# ============================================================
# SYSTEM INSTRUCTIONS
# ============================================================

SYSTEM_INSTRUCTIONS = """
You are TechWise, a software engineering decision assistant.

Your purpose is to help developers make and review technology
and architecture decisions.

You have access to three custom tools:

1. Decision Recorder
2. Decision Retriever
3. Decision Impact Analyzer

You also have access to Google Search for current web research.

Use tools dynamically based on the user's request.

Do NOT automatically call every tool.

============================================================
DECISION MEMORY
============================================================

Use the decision retriever when the user asks about an
existing decision or when a previous decision is relevant
to the question.

Never invent stored decisions.

============================================================
WEB RESEARCH
============================================================

Use Google Search when current or external information would
improve the answer.

Examples include:

- Current technology capabilities
- Current framework features
- Current library versions
- Current cloud/platform support
- Current industry practices
- Technology comparisons
- Recent changes in software technologies
- Current documentation
- Current official recommendations

Prefer reliable and authoritative sources such as:

- Official documentation
- Official technology websites
- Official cloud/provider documentation
- Reputable technical sources

Do not use web search when it is unnecessary for a simple
question that can be answered reliably without current data.

When web research is used, incorporate the relevant findings
into the recommendation and preserve the source citations
provided by Gemini.

============================================================
IMPACT ANALYSIS
============================================================

When a changed requirement is being evaluated:

1. Identify the relevant previous decision.
2. Retrieve the stored decision.
3. Understand the original context.
4. Understand the original reason.
5. Understand the alternatives.
6. Understand the consequences.
7. Understand the new requirement.
8. Identify what changed.
9. Determine whether the original reason is still valid.
10. Use Google Search when current technical information
    is useful.
11. Compare the existing technology with relevant alternatives.
12. Make the final recommendation.

============================================================
RECOMMENDATIONS
============================================================

For technical recommendations, use this format:

Recommendation: KEEP / RECONSIDER / REPLACE

Reason:
Explain why.

Web Research:
Summarize important current findings when web research
was used.

Trade-offs:
Explain the important advantages and disadvantages.

Suggested next step:
Give a practical next action.

============================================================
IMPORTANT
============================================================

Do not record a new decision unless the user explicitly
asks you to save or record it.

A recommendation is NOT automatically a new decision.

If the user asks for a new recommendation and there is no
stored decision, provide a recommendation based on your
software engineering knowledge and use Google Search when
current information would materially improve the answer.

Be concise, practical, and technically accurate.
"""


# ============================================================
# AGENT LOOP
# ============================================================

def run_agent(user_message):

    interaction = client.interactions.create(
        model=MODEL,
        input=user_message,
        system_instruction=SYSTEM_INSTRUCTIONS,
        tools=tools
    )

    while True:

        function_calls = [
            step
            for step in interaction.steps
            if step.type == "function_call"
        ]

        # If there are no custom function calls,
        # return Gemini's final response.
        if not function_calls:

            return interaction.output_text

        function_results = []

        for call in function_calls:

            tool_name = call.name
            arguments = call.arguments

            try:

                result = execute_tool(
                    tool_name,
                    arguments
                )

            except Exception as error:

                result = {
                    "success": False,
                    "error": str(error)
                }

            function_results.append({
                "type": "function_result",
                "name": tool_name,
                "call_id": call.id,
                "result": [
                    {
                        "type": "text",
                        "text": json.dumps(result)
                    }
                ]
            })

        # Continue the same Gemini interaction after
        # executing the custom function tools.
        interaction = client.interactions.create(
            model=MODEL,
            previous_interaction_id=interaction.id,
            input=function_results,
            system_instruction=SYSTEM_INSTRUCTIONS,
            tools=tools
        )


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":

    print("TechWise Gemini Agent")
    print("-" * 40)

    while True:

        user_message = input("\nYou: ")

        if user_message.lower() in [
            "exit",
            "quit"
        ]:
            break

        try:

            response = run_agent(
                user_message
            )

            print("\nTechWise:")
            print(response)

        except Exception as error:

            print("\nError:")
            print(error)