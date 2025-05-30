import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

class Post:
    def __init__(self, id: int, title: str, body: str):
        self.id = id
        self.title = title
        self.body = body

class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.posts: list[Post] = []

    def add_post(self, post: Post):
        self.posts.append(post)

    def average_title_length(self) -> float:
        if not self.posts:
            return 0.0
        total_length = sum(len(post.title) for post in self.posts)
        return total_length / len(self.posts)

    def average_body_length(self) -> float:
        if not self.posts:
            return 0.0
        total_length = sum(len(post.body) for post in self.posts)
        return total_length / len(self.posts)

class BlogAnalytics:
    def __init__(self):
        self.users: list[User] = []

    def fetch_data(self):
        try:
            users_response = requests.get(f"{BASE_URL}/users")
            users_response.raise_for_status()
            users_data = users_response.json()

            for user_data in users_data:
                posts_response = requests.get(f"{BASE_URL}/posts?userId={user_data['id']}")
                posts_response.raise_for_status()
                posts_data = posts_response.json()

                user = User(user_data["id"], user_data["name"])
                for post_data in posts_data:
                    post = Post(post_data["id"], post_data["title"], post_data["body"])
                    user.add_post(post)
                self.users.append(user)

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            raise

    def user_with_longest_average_body(self) -> User:
        if not self.users:
            raise ValueError("No users available to analyze")
        return max(self.users, key=lambda user: user.average_body_length())

    def users_with_many_long_titles(self) -> list[User]:
        return [
            user for user in self.users
            if sum(1 for post in user.posts if len(post.title) > 40) > 5
        ]

# Example usage
if __name__ == "__main__":
    analytics = BlogAnalytics()
    analytics.fetch_data()

    # User with the longest average post body length
    longest_body_user = analytics.user_with_longest_average_body()
    print(f"User with longest average body length: {longest_body_user.name}")
    print(f"Average body length: {longest_body_user.average_body_length():.2f}")

    # Users with more than 5 posts with titles longer than 40 characters
    users_with_long_titles = analytics.users_with_many_long_titles()
    print("\nUsers with more than 5 posts with titles longer than 40 chars:")
    for user in users_with_long_titles:
        print(f"- {user.name}")
