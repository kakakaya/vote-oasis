from flask import Flask, jsonify, request

from . import youtube_api

# Imports the Cloud Logging client library


# client = google.cloud.logging.Client()
# client.setup_logging()


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        link_to_get_youtube_comments = "http://localhost:5000/get_youtube_comments"
        return (
            "<p>Hello, World!</p>"
            "<p>Click <a href='"
            + link_to_get_youtube_comments
            + "'>here</a> to get YouTube comments.</p>"
        )

    @app.route("/get_youtube_comments", methods=["POST"])
    def get_youtube_comments():
        youtube = youtube_api.YouTubeAPI()
        try:
            data = request.get_json()
            youtube_id = data.get("youtube_id")

            if not youtube_id:
                return jsonify({"error": "Missing youtube_id"}), 400

            messages = youtube.list_live_comments(youtube_id)

            if messages:
                return jsonify(
                    {"status": "success", "message_count": len(messages)}
                ), 200
            return jsonify(
                {
                    "status": "failed",
                    "message": "Could not retrieve live chat messages.",
                },
            ), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0")
