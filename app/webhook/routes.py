from flask import Blueprint, request, jsonify
from app.extensions import mongo
from datetime import datetime

webhook = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    try:
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')

        author = "N/A"
        action = "UNKNOWN"
        from_branch = "N/A"
        to_branch = "N/A"
        request_id = "N/A"
        timestamp = datetime.utcnow().isoformat() + "Z"

        if event_type == 'push':
            action = "PUSH"
            author = data.get("pusher", {}).get("name", "N/A")
            to_branch = data.get("ref", "").split("/")[-1]
            request_id = data.get("after", "N/A")
            if data.get("head_commit"):
                timestamp = data["head_commit"].get("timestamp", timestamp)

        elif event_type == 'pull_request':
            pr = data.get("pull_request", {})
            pr_action = data.get("action", "")
            author = pr.get("user", {}).get("login", "N/A")
            from_branch = pr.get("head", {}).get("ref", "N/A")
            to_branch = pr.get("base", {}).get("ref", "N/A")
            request_id = str(pr.get("number", "N/A"))
            timestamp = pr.get("updated_at", timestamp)

            if pr.get("merged") and pr_action == "closed":
                action = "MERGE"
            else:
                action = "PULL_REQUEST"

        payload = {
            "request_id": request_id,
            "author": author,
            "action": action,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

        mongo.db.actions.insert_one(payload)
        return jsonify({"status": "stored", "data": payload}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional endpoint for frontend polling
@webhook.route('/api/actions', methods=["GET"])
def get_actions():
    try:
        actions = list(mongo.db.actions.find().sort("timestamp", -1).limit(10))
        for action in actions:
            action["_id"] = str(action["_id"])  # Convert ObjectId to string
        return jsonify(actions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
