import json

from flask import Blueprint, Response, jsonify, request, stream_with_context
from pydantic import ValidationError

from models.schemas import AdvisorRequest, UserProfile
from services.financial_advisor import ask_question, get_recommendations
from services.investment_analyzer import get_investment_insights
from services.planner import get_financial_plan, stream_financial_plan
from services.chart_generator import (
    charts_for_recommendations,
    charts_for_investment_insights,
    charts_for_financial_plan,
)

api = Blueprint("api", __name__, url_prefix="/api")


def _parse_profile(data: dict) -> UserProfile:
    req = AdvisorRequest(**data)
    return req.profile, req.question


@api.route("/recommendations", methods=["POST"])
def recommendations():
    try:
        profile, _ = _parse_profile(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    result = get_recommendations(profile)
    data = result.model_dump()
    data["charts"] = charts_for_recommendations(profile)
    return jsonify(data)


@api.route("/investment-insights", methods=["POST"])
def investment_insights():
    try:
        profile, _ = _parse_profile(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    result = get_investment_insights(profile)
    data = result.model_dump()
    data["charts"] = charts_for_investment_insights(profile)
    return jsonify(data)


@api.route("/financial-plan", methods=["POST"])
def financial_plan():
    try:
        profile, _ = _parse_profile(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    result = get_financial_plan(profile)
    data = result.model_dump()
    data["charts"] = charts_for_financial_plan(profile)
    return jsonify(data)


@api.route("/financial-plan/stream", methods=["POST"])
def financial_plan_stream():
    try:
        profile, _ = _parse_profile(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    def event_stream():
        for token in stream_financial_plan(profile):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
    )


@api.route("/ask", methods=["POST"])
def ask():
    try:
        profile, question = _parse_profile(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    if not question:
        return jsonify({"error": "question field is required"}), 400

    result = ask_question(profile, question)
    return jsonify(result.model_dump())


@api.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
