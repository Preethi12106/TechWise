import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from decision_recorder import record_decision
from decision_retriever import retrieve_decisions
from decision_impact_analyzer import analyze_impact


# Load API key
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found")

client = OpenAI(api_key=api_key)


# -----------------------------
# TOOL FUNCTIONS
# -----------------------------

def record_decision_tool(
    decision,
    context,
    reason,
    alternatives,
    consequences
):
    decision_id = record_decision(
        decision,
        context,
        reason,
        alternatives,
        consequences
    )

    return {
        "success": True,
        "decision_id": decision_id
    }


def retrieve_decisions_tool(keyword):

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


def analyze_impact_tool(decision_id, new_requirement):

    result = analyze_impact(
        decision_id,
        new_requirement
    )

    if result is None:
        return {
            "success": False,
            "message": "Decision not found"
        }

    return result


# -----------------------------
# TOOL DEFINITIONS
# -----------------------------

tools = [

    {
        "type": "function",
        "name": "record_decision",
        "description": "Record a software engineering decision in persistent memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "decision": {
                    "type": "string"
                },
                "context": {
                    "type": "string"
                },
                "reason": {
                    "type": "string"
                },
                "alternatives": {
                    "type": "string"
                },
                "consequences": {
                    "type": "string"
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
    },

    {
        "type": "function",
        "name": "retrieve_decisions",
        "description": "Search persistent memory for previous software engineering decisions.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string"
                }
            },
            "required": ["keyword"]
        }
    },

    {
        "type": "function",
        "name": "analyze_impact",
        "description": "Retrieve a previous decision and compare it with a new project requirement.",
        "parameters": {
            "type": "object",
            "properties": {
                "decision_id": {
                    "type": "integer"
                },
                "new_requirement": {
                    "type": "string"
                }
            },
            "required": [
                "decision_id",
                "new_requirement"
            ]
        }
    }
]


# -----------------------------
# EXECUTE TOOL
# -----------------------------

def execute_tool(name, arguments):

    if name == "record_decision":
        return record_decision_tool(**arguments)

    elif name == "retrieve_decisions":
        return retrieve_decisions_tool(**arguments)

    elif name == "analyze_impact":
        return analyze_impact_tool(**arguments)

    else:
        return {
            "error": f"Unknown tool: {name}"
        }


# -----------------------------
# AGENT
# -----------------------------

def run_agent(user_message):

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": (
                    "You are TechWise, an AI software engineering "
                    "decision assistant. You help developers record, "
                    "retrieve, and evaluate software engineering decisions. "
                    "Use the available tools whenever they are relevant. "
                    "Do not invent information that is not stored in memory."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        tools=tools
    )

    # Check whether the LLM requested a tool
    for item in response.output:

        if item.type == "function_call":

            tool_name = item.name

            arguments = json.loads(item.arguments)

            print(f"\nTool selected: {tool_name}")
            print(f"Arguments: {arguments}")

            tool_result = execute_tool(
                tool_name,
                arguments
            )

            # Send tool result back to the LLM
            second_response = client.responses.create(
                model="gpt-5.6-luna",
                previous_response_id=response.id,
                input=[
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(tool_result)
                    }
                ]
            )

            return second_response.output_text

    return response.output_text


# -----------------------------
# CHAT LOOP
# -----------------------------

if __name__ == "__main__":

    print("===================================")
    print("       TechWise AI Agent")
    print("===================================")
    print("Type 'exit' to stop.\n")

    while True:

        user_message = input("You: ")

        if user_message.lower() == "exit":
            break

        answer = run_agent(user_message)

        print("\nTechWise:", answer)
        print()