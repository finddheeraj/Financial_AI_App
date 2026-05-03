import re
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedAction:
    tool_name: str
    tool_input: dict = field(default_factory=dict)


@dataclass
class ParseResult:
    thought: Optional[str] = None
    action: Optional[ParsedAction] = None
    final_answer: Optional[str] = None
    raw: str = ""


def parse_agent_output(text: str) -> ParseResult:
    result = ParseResult(raw=text)
    text = text.strip()
    if not text:
        result.final_answer = ""
        return result

    thought_match = re.search(
        r"Thought\s*:\s*(.+?)(?=\n\s*(?:Action|Final\s*Answer)\s*:|\Z)",
        text, re.DOTALL | re.IGNORECASE,
    )
    if thought_match:
        result.thought = thought_match.group(1).strip()

    final_match = re.search(
        r"Final\s*Answer\s*:\s*(.+)", text, re.DOTALL | re.IGNORECASE
    )
    if final_match:
        result.final_answer = final_match.group(1).strip()
        return result

    action_match = re.search(r"Action\s*:\s*(\S+)", text, re.IGNORECASE)
    input_match = re.search(
        r"Action\s*Input\s*:\s*(.+?)(?=\n\s*(?:Thought|Observation|Final\s*Answer)\s*:|\Z)",
        text, re.DOTALL | re.IGNORECASE,
    )

    if action_match:
        tool_name = action_match.group(1).strip()
        tool_input = {}
        if input_match:
            tool_input = _parse_json_fuzzy(input_match.group(1).strip())
        result.action = ParsedAction(tool_name=tool_name, tool_input=tool_input)
        return result

    if not result.thought and not result.action:
        result.final_answer = text

    return result


def _parse_json_fuzzy(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    brace_match = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    cleaned = raw.replace("'", '"')
    cleaned = re.sub(r",\s*}", "}", cleaned)
    cleaned = re.sub(r",\s*]", "]", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    kv_pairs = re.findall(r"(\w+)\s*[=:]\s*[\"']?([\w.]+)[\"']?", raw)
    if kv_pairs:
        result = {}
        for k, v in kv_pairs:
            try:
                result[k] = float(v) if "." in v else int(v)
            except ValueError:
                result[k] = v
        return result

    return {}
