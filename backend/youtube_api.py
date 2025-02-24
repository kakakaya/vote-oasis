import datetime
import os

import googleapiclient.discovery
import googleapiclient.errors


class YouTubeAPI:
    """A singleton class for interacting with the YouTube Data API."""

    def __init__(self) -> None:
        api_key = os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            msg = "YOUTUBE_API_KEY environment variable not set."
            raise ValueError(msg)
        self._youtube = googleapiclient.discovery.build(
            "youtube",
            "v3",
            developerKey=api_key,
        )

    def list_live_comments(self, video_id: str, max_results=20) -> list:
        youtube = self._youtube
        try:
            video_response = (
                youtube.videos()
                .list(
                    part="liveStreamingDetails",
                    id=video_id,
                )
                .execute()
            )

            if not video_response["items"]:
                self.logger.warning(f"No live stream found for video ID: {video_id}")
                return None

            live_details = video_response["items"][0]["liveStreamingDetails"]
            live_chat_id = live_details["activeLiveChatId"]

            chat_response = (
                youtube.liveChatMessages()
                .list(
                    liveChatId=live_chat_id,
                    part="snippet,authorDetails",
                    maxResults=max_results,
                )
                .execute()
            )

            # 結果表示
            print(f"最新{chat_response['pageInfo']['resultsPerPage']}件のチャット:")
            for item in chat_response["items"]:
                author = item["authorDetails"]["displayName"]
                author_id = item["authorDetails"]["channelId"]
                message = item["snippet"]["displayMessage"]
                time_str = item["snippet"]["publishedAt"]

                is_verified = item["authorDetails"]["isVerified"]
                is_chat_owner = item["authorDetails"]["isChatOwner"]
                # is_chat_sponsor = item["authorDetails"]["isChatSponsor"]
                is_chat_moderator = item["authorDetails"]["isChatModerator"]
                time = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f%z")
                print(
                    f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {author} ({author_id}):"
                    f" {message}, verified: {is_verified},"
                    f" owner: {is_chat_owner}, moderator: {is_chat_moderator}",
                )
            return chat_response["items"]

        except Exception as e:
            print(f"Error at list_live_comments: {e!s}")
            return []
