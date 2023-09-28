import praw
import re
import time
from pushbullet import Pushbullet
import keys


class RedditScanner:
    def __init__(self, subreddit, regex, parameters):
        self.subreddit_name = subreddit
        self.regex = regex
        self.parameters = parameters
        self.last_post_time = 0
        self.last_post_time_available = False
        self.reddit = praw.Reddit(
            client_id=keys.reddit_client_id,
            client_secret=keys.reddit_client_secret,
            user_agent="bestdeals",
        )

    def _matches_criteria(self, title, flair):
        if flair not in ["Selling", "Selling\\Trading"]:
            return False
        # if re.search(self.regex, title):
        #     return True
        if any(param in title for param in self.parameters):
            return True
        return False

    def scan_new_posts(self):
        pb = Pushbullet(keys.PUSHBULLET_ACCESS_TOKEN)
        if not self.last_post_time_available:
            for submission in self.reddit.subreddit(self.subreddit_name).new(limit=None):
                if self._matches_criteria(submission.title.lower(), submission.link_flair_text):
                    self.last_post_time = submission.created_utc
                    self.last_post_time_available = True
                    print(f"title: {submission.title}\nurl: {submission.url}\n")
                    pb.push_note(submission.title, submission.url)
                    break
        else:
            posts_to_notify = []
            for submission in self.reddit.subreddit(self.subreddit_name).new(limit=None):
                if submission.created_utc <= self.last_post_time:
                    break
                if self._matches_criteria(submission.title.lower(), submission.link_flair_text):
                    posts_to_notify.append(submission)

            for post in reversed(posts_to_notify):
                print(f"title: {post.title}\nurl: {post.url}\n")
                pb.push_note(post.title, post.url)
            if posts_to_notify:
                self.last_post_time = posts_to_notify[-1].created_utc


def main():
    scanner = RedditScanner(
        subreddit="CanadianHardwareSwap",
        regex=r"[\d]{4,5}",
        parameters=["ryzen", "5600", "5600x"]
    )

    while True:
        scanner.scan_new_posts()
        time.sleep(300)


if __name__ == '__main__':
    main()
