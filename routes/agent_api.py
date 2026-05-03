import json
import uuid

from flask import Blueprint, Response, jsonify, request, stream_with_context
from pydantic import ValidationError

from models.schemas import UserProfile
from prompts.templates import build_profile_summary
from agent.loop import run_agent
from memory.session import get_session_store

agent_api = Blueprint("agent_api", __name__, url_prefix="/api/agent")


@agent_api.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    session_id = data.get("session_id") or str(uuid.uuid4())
    message = data.get("message", "").strip()
    profile_data = data.get("profile")

    if not message:
        return jsonify({"error": "message is required"}), 400

    store = get_session_store()

    if profile_data:
        try:
            profile = UserProfile(**profile_data)
            store.set_profile(session_id, profile_data)
        except ValidationError as e:
            return jsonify({"error": e.errors()}), 400
    else:
        profile_data = store.get_profile(session_id)
        if not profile_data:
            return jsonify({"error": "No profile found. Send profile with first message."}), 400
        profile = UserProfile(**profile_data)

    profile_summary = build_profile_summary(profile)

    def event_stream():
        yield f"event: session\ndata: {json.dumps({'session_id': session_id})}\n\n"

        for step in run_agent(session_id, profile_summary, message, store):
            event_type = step["type"]
            payload = json.dumps({"content": step["content"]})
            yield f"event: {event_type}\ndata: {payload}\n\n"

        yield "event: done\ndata: {}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
