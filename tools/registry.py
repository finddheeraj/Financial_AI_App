from dataclasses import dataclass, field
from typing import Callable, Any, Optional


@dataclass
class ToolParameter:
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: list[ToolParameter]
    func: Callable = field(repr=False, default=None)


_REGISTRY: dict[str, ToolDefinition] = {}


def tool(name: str, description: str, parameters: list[dict]):
    def decorator(func):
        params = [ToolParameter(**p) for p in parameters]
        _REGISTRY[name] = ToolDefinition(
            name=name, description=description, parameters=params, func=func
        )
        return func
    return decorator


def get_tool(name: str) -> Optional[ToolDefinition]:
    return _REGISTRY.get(name)


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    td = _REGISTRY.get(name)
    if td is None:
        return f"Error: Unknown tool '{name}'. Available: {list(_REGISTRY.keys())}"
    try:
        coerced = {}
        for param in td.parameters:
            if param.name in arguments:
                val = arguments[param.name]
                if param.type == "float":
                    val = float(val)
                elif param.type == "int":
                    val = int(float(val))
                elif param.type == "str":
                    val = str(val)
                coerced[param.name] = val
            elif param.required:
                return f"Error: Missing required parameter '{param.name}' for tool '{name}'."
            elif param.default is not None:
                coerced[param.name] = param.default
        result = td.func(**coerced)
        return str(result)
    except Exception as e:
        return f"Error executing '{name}': {e}"


def build_tool_descriptions() -> str:
    lines = []
    for name, td in _REGISTRY.items():
        param_parts = []
        for p in td.parameters:
            req = "required" if p.required else f"optional, default={p.default}"
            param_parts.append(f"    - {p.name} ({p.type}, {req}): {p.description}")
        lines.append(f"- {name}: {td.description}")
        lines.append("  Parameters:")
        lines.extend(param_parts)
    return "\n".join(lines)
