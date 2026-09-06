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
    context="",
    reason="",
    alternatives="",
    consequences=""
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
        "type": "web_search"
    },

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
            "required": ["decision"]
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
    tool_handlers = {
        "record_decision": record_decision_tool,
        "retrieve_decisions": retrieve_decisions_tool,
        "analyze_impact": analyze_impact_tool,
    }

    handler = tool_handlers.get(name)

    if handler is None:
        return {"success": False, "error": f"Unknown tool: {name}"}

    try:
        return handler(**arguments)
    except (TypeError, ValueError, KeyError) as error:
        return {
            "success": False,
            "error": f"Invalid arguments for {name}: {error}"
        }
    except Exception as error:
        return {
            "success": False,
            "error": f"{name} failed: {error}"
        }


# -----------------------------
# AGENT
# -----------------------------

def run_agent(user_message):

    instructions = (
        "You are TechWise, an AI software engineering decision assistant.\n"
        "You help developers record software engineering decisions, retrieve historical "
        "decisions, evaluate them against changed requirements, research current technical "
        "information, and provide independent recommendations.\n\n"
        "Persistent SQLite memory represents historical project decisions. Web search "
        "represents current or external technical information. Reason over these sources; "
        "do not invent facts or claim that a recommendation came from memory.\n\n"
        "Use persistent memory when the user asks about a previous decision or when a new "
        "requirement may affect an existing decision. Use web search only when current or "
        "external information is useful. Use both when evaluating a historical decision and "
        "current information matters. Do not use tools unnecessarily.\n\n"
        "For a changed requirement, identify the relevant historical decision, retrieve it, "
        "compare its original context and reasoning with the new requirement, and use the "
        "analyze_impact tool as evidence. The analyzer does not decide the outcome; you do.\n\n"
        "Clearly distinguish historical information from memory, current information from "
        "web research, and your recommendation. When giving a technical recommendation, "
        "use exactly this structure:\n"
        "Recommendation: KEEP, RECONSIDER, or REPLACE\n"
        "Reason: explain the evidence and reasoning\n"
        "Trade-offs: explain important advantages and disadvantages\n"
        "Suggested next step: give a practical action\n"
        "Use KEEP when the original decision still fits, RECONSIDER when important trade-offs "
        "need evaluation, and REPLACE when it is no longer a good fit. Do not choose arbitrarily.\n\n"
        "A recommendation is not automatically a decision. Never modify or overwrite a "
        "historical decision unless the user explicitly asks to record a new decision. "
        "For simple retrieval questions, answer from stored evidence without unnecessary web search."
    )

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=instructions,
        input=user_message,
        tools=tools
    )

    while True:

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # No more tools needed → final answer
        if not tool_calls:
            return response.output_text

        tool_outputs = []

        for item in tool_calls:

            tool_name = item.name

            try:
                arguments = json.loads(item.arguments)
            except (TypeError, json.JSONDecodeError) as error:
                tool_result = {
                    "success": False,
                    "error": f"Invalid JSON arguments for {tool_name}: {error}"
                }
                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(tool_result)
                })
                continue

            tool_result = execute_tool(
                tool_name,
                arguments
            )

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(tool_result)
            })

        # Send tool results back to the LLM
        response = client.responses.create(
            model="gpt-5.6-luna",
            previous_response_id=response.id,
            instructions=instructions,
            input=tool_outputs,
            tools=tools
        )
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