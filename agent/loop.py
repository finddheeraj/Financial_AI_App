import json
import re
from typing import Generator

from agent.parser import parse_agent_output
from agent.prompt import build_agent_system_prompt, build_agent_user_message
from tools.registry import execute_tool
from config import Config


def _strip_chart_data(text):
    return re.sub(r'\[CHART_DATA\].*?\[/CHART_DATA\]', '', text, flags=re.DOTALL).rstrip()


STEP_THOUGHT = "thought"
STEP_TOOL_CALL = "tool_call"
STEP_TOOL_RESULT = "tool_result"
STEP_ANSWER = "answer"
STEP_ERROR = "error"


def run_agent(
    session_id: str,
    profile_summary: str,
    question: str,
    session_store,
) -> Generator[dict, None, None]:
    from services.llm_service import chat_completion

    max_iterations = getattr(Config, "AGENT_MAX_ITERATIONS", 5)
    step_tokens = getattr(Config, "AGENT_STEP_TOKENS", 300)

    system_prompt = build_agent_system_prompt()
    user_message = build_agent_user_message(profile_summary, question)

    messages = [{"role": "system", "content": system_prompt}]

    history = session_store.get_history(session_id, last_n=3)
    for entry in history:
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["assistant"]})

    messages.append({"role": "user", "content": user_message})

    final_answer_text = None

    for _ in range(max_iterations):
        try:
            llm_output = chat_completion(
                messages=messages,
                max_tokens=step_tokens,
                temperature=Config.TEMPERATURE,
                top_p=Config.TOP_P,
                stop=["Observation:", "Observation :"],
            )
        except Exception as e:
            yield {"type": STEP_ERROR, "content": f"LLM error: {e}"}
            return

        parsed = parse_agent_output(llm_output)

        if parsed.thought:
            yield {"type": STEP_THOUGHT, "content": parsed.thought}

        if parsed.final_answer is not None:
            final_answer_text = parsed.final_answer
            yield {"type": STEP_ANSWER, "content": parsed.final_answer}
            break

        if parsed.action:
            yield {
                "type": STEP_TOOL_CALL,
                "content": json.dumps({
                    "tool": parsed.action.tool_name,
                    "input": parsed.action.tool_input,
                }),
            }

            tool_result = execute_tool(
                parsed.action.tool_name, parsed.action.tool_input
            )
            yield {"type": STEP_TOOL_RESULT, "content": tool_result}

            messages.append({"role": "assistant", "content": llm_output})
            messages.append({"role": "user", "content": f"Observation: {_strip_chart_data(tool_result)}"})
            continue

        final_answer_text = llm_output
        yield {"type": STEP_ANSWER, "content": llm_output}
        break
    else:
        yield {
            "type": STEP_ANSWER,
            "content": "I've completed my analysis but reached the iteration limit. "
                       "Please review the tool results above for detailed numbers.",
        }

    if final_answer_text:
        session_store.add_exchange(session_id, question, final_answer_text)
