import requests
import json
from collections import defaultdict

BASE_URL = "https://jsonplaceholder.typicode.com"


class Comment:
    def __init__(self, id: int, post_id: int, name: str, email: str, body: str):
        self.id = id
        self.post_id = post_id
        self.name = name
        self.email = email
        self.body = str(body)  # body is always a string


class CommentModerator:
    def __init__(self):
        self.comments: list[Comment] = []
        self.flagged_comments: list[Comment] = []

    def fetch_comments(self):
        try:
            response = requests.get(f"{BASE_URL}/comments")
            response.raise_for_status()  # Check for HTTP errors

            comments_data = response.json()
            if not comments_data:
                print("No comments received from API")
                return False

            for comment_data in comments_data:
                try:
                    comment = Comment(
                        int(comment_data["id"]),
                        int(comment_data["postId"]),
                        str(comment_data["name"]),
                        str(comment_data["email"]),
                        str(comment_data["body"]),
                    )
                    self.comments.append(comment)
                except (KeyError, ValueError) as e:
                    print(f"Skipping malformed comment: {e}")
                    continue

            print(f"Successfully fetched {len(self.comments)} comments")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch comments: {e}")
            return False

    def is_suspicious(self, comment: Comment) -> bool:
        spam_keywords = ["buy", "free", "offer", "!!!", "???"]
        body = comment.body.lower()
        return any(keyword in body for keyword in spam_keywords)

    def flag_suspicious_comments(self):
        if not self.comments:
            if not self.fetch_comments():
                return []

        self.flagged_comments = [
            comment for comment in self.comments
            if self.is_suspicious(comment)
        ]
        print(f"Flagged {len(self.flagged_comments)} suspicious comments")
        return self.flagged_comments

    def group_by_post(self) -> dict[int, list[Comment]]:
        grouped = defaultdict(list)
        for comment in self.flagged_comments:
            grouped[comment.post_id].append(comment)
        return dict(grouped)

    def top_spammy_emails(self, n: int = 5) -> list[str]:
        email_counts = defaultdict(int)
        for comment in self.flagged_comments:
            email_counts[comment.email] += 1

        return sorted(
            email_counts.keys(),
            key=lambda email: email_counts[email],
            reverse=True
        )[:n]

    def export_flagged_to_json(self, filename: str = "flagged_comments.json"):
        if not self.flagged_comments:
            self.flag_suspicious_comments()

        export_data = [
            {
                "id": c.id,
                "post_id": c.post_id,
                "name": c.name,
                "email": c.email,
                "body": c.body
            }
            for c in self.flagged_comments
        ]

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"Exported {len(export_data)} comments to {filename}")


if __name__ == "__main__":
    moderator = CommentModerator()

    # Complete processing sequence
    if moderator.fetch_comments():
        moderator.flag_suspicious_comments()

        grouped = moderator.group_by_post()
        print(f"\nComments grouped by post (total posts: {len(grouped)}):")
        for post_id, comments in grouped.items():
            print(f"Post {post_id}: {len(comments)} flagged comments")

        top_emails = moderator.top_spammy_emails()
        print("\nTop spammy emails:")
        for i, email in enumerate(top_emails, 1):
            print(f"{i}. {email}")

        moderator.export_flagged_to_json()
