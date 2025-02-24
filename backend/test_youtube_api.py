import os
from unittest.mock import Mock, patch

import googleapiclient.errors
import pytest

from backend.app import create_app
from backend.youtube_api import YouTubeAPI


def test_youtube_api_no_api_key() -> None:
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError) as e:
            assert os.environ == {}
            YouTubeAPI()
    assert str(e.value) == "YOUTUBE_API_KEY environment variable not set."


class TestYouTubeAPI:
    # Override os.environ["YOUTUBE_API_KEY"] before each test
    # @pytest.fixture
    def setup_method(self) -> None:
        os.environ["YOUTUBE_API_KEY"] = "test_key"

    @pytest.fixture
    def app(self):
        app = create_app()
        app.config["TESTING"] = True
        return app

    def test_youtube_api_init(self) -> None:
        youtube = YouTubeAPI()
        assert youtube._youtube is not None

    @pytest.mark.xfail(reason="Singleton instance not implemented")
    @patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"})
    def test_youtube_api_init_single_instance(self) -> None:
        youtube1 = YouTubeAPI()
        youtube2 = YouTubeAPI()
        assert youtube1 is youtube2

    @patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"})
    @patch("backend.youtube_api.googleapiclient.discovery.build")
    def test_youtube_api_list_live_comments(self, mock_build) -> None:
        youtube = YouTubeAPI()
        youtube_id = "test_video_id"
        max_results = 20

        youtube._youtube.videos().list().execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": "test_live_chat_id",
                    },
                },
            ],
        }

        chat_content = {
            "authorDetails": {
                "displayName": "test_author",
                "channelId": "test_channel_id",
                "isVerified": True,
                "isChatOwner": False,
                "isChatSponsor": False,
                "isChatModerator": False,
            },
            "snippet": {
                "displayMessage": "test_message",
                "publishedAt": "2025-01-01T00:00:00.12345Z",
            },
        }
        youtube._youtube.liveChatMessages().list().execute.return_value = {
            "pageInfo": {"resultsPerPage": max_results},
            "items": [chat_content for _ in range(max_results)],
        }

        messages = youtube.list_live_comments(youtube_id, max_results)
        assert messages is not None
        assert len(messages) == max_results

    @patch("backend.youtube_api.YouTubeAPI")
    def test_list_live_comments(self, mock_youtube_api, app) -> None:
        assert os.environ.get("YOUTUBE_API_KEY") == "test_key"
        mock_youtube_api.return_value.list_live_comments.return_value = [
            {
                "authorDetails": {
                    "displayName": "test_author",
                    "channelId": "test_channel_id",
                    "isVerified": True,
                    "isChatOwner": False,
                    "isChatSponsor": False,
                    "isChatModerator": False,
                },
                "snippet": {
                    "displayMessage": "test_message",
                    "publishedAt": "2024-02-24T12:00:00.000Z",
                },
            },
        ]

        with app.test_client() as client:
            with client.post(
                "/get_youtube_comments",
                json={"youtube_id": "test_video_id"},
            ) as response:
                assert response.status_code == 200
                assert response.json["message_count"] == 1

    @patch("backend.youtube_api.YouTubeAPI")
    def test_list_live_comments_no_video(self, mock_youtube_api, app) -> None:
        mock_youtube_api.return_value.list_live_comments.return_value = []

        with app.test_client() as client:
            response = client.post(
                "/get_youtube_comments",
                json={"youtube_id": "test_video_id"},
            )
            assert response.content_type == "application/json"
            assert response.status_code != 200
            assert response.json["message"] == "Could not retrieve live chat messages."

    @patch("backend.youtube_api.YouTubeAPI")
    def test_list_live_comments_api_error(self, mock_youtube_api, app) -> None:
        mock_youtube_api.return_value.list_live_comments.side_effect = (
            googleapiclient.errors.HttpError(Mock(status=403), b"test error")
        )
        with app.test_client() as client:
            response = client.post(
                "/get_youtube_comments",
                json={"youtube_id": "test_video_id"},
            )
            assert response.status_code == 500
            assert 'test error' in response.json["error"]
