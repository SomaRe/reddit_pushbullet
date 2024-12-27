import praw
import re
import time
from pushbullet import API
import keys

class RedditScanner:
    """
    A class to scan a specified subreddit for new posts matching given criteria and send notifications.

    Attributes:
        subreddit_name (str): The name of the subreddit to scan.
        regex (str or None): The regex pattern to match in post titles. Ignored if None.
        parameters (list): A list of mandatory strings to match in post titles. At least one is required.
        flairs (list or None): A list of acceptable flairs to filter posts. Ignored if None.
        last_post_time (float): The timestamp of the last scanned post.
        last_post_time_available (bool): Flag indicating whether the last post time is set.
        reddit (praw.Reddit): The Reddit client object.
        pb (Pushbullet): The Pushbullet client object for sending notifications.
    """

    def __init__(self, subreddit, regex=None, parameters=None, flairs=None):
        """
        Initializes the RedditScanner instance with the specified subreddit, regex pattern, parameters, and flairs.

        Args:
            subreddit (str): The name of the subreddit to scan.
            regex (str or None): The regex pattern to match in post titles. Ignored if None.
            parameters (list): A list of mandatory strings to match in post titles. At least one is required.
            flairs (list or None): A list of acceptable flairs to filter posts. Ignored if None.

        Raises:
            ValueError: If `parameters` is None or empty.
        """
        if not parameters or not isinstance(parameters, list) or len(parameters) == 0:
            raise ValueError("At least one search term must be provided in 'parameters'.")

        self.subreddit_name = subreddit
        self.regex = regex
        self.parameters = parameters
        self.flairs = flairs
        self.last_post_time = 0
        self.last_post_time_available = False
        self.reddit = praw.Reddit(
            client_id=keys.reddit_client_id,
            client_secret=keys.reddit_client_secret,
            user_agent=keys.USER_AGENT
        )
        self.pb = API()
        self.pb.set_token(keys.PUSHBULLET_ACCESS_TOKEN)

    def _matches_criteria(self, title, flair):
        """
        Checks whether a post matches the specified criteria.

        Args:
            title (str): The title of the post.
            flair (str): The flair of the post.

        Returns:
            bool: True if the post matches the criteria, False otherwise.
        """
        # Check flairs if provided
        if self.flairs and flair not in self.flairs:
            return False

        # Check regex if provided
        if self.regex and re.search(self.regex, title):
            return True

        # Check mandatory parameters
        if any(param in title for param in self.parameters):
            return True

        return False

    def scan_new_posts(self):
        """
        Scans the subreddit for new posts and sends notifications for posts that match the criteria.
        """
        if not self.last_post_time_available:
            # Initialize last_post_time by scanning the most recent matching post.
            for submission in self.reddit.subreddit(self.subreddit_name).new(limit=None):
                if self._matches_criteria(submission.title.lower(), submission.link_flair_text):
                    self.last_post_time = submission.created_utc
                    self.last_post_time_available = True
                    print(f"title: {submission.title}\nurl: {submission.url}\n")
                    self.pb.send_note(submission.title, submission.url)
                    break
        else:
            # Collect and notify about new posts since the last scanned time.
            posts_to_notify = []
            for submission in self.reddit.subreddit(self.subreddit_name).new(limit=None):
                if submission.created_utc <= self.last_post_time:
                    break
                if self._matches_criteria(submission.title.lower(), submission.link_flair_text):
                    posts_to_notify.append(submission)

            for post in reversed(posts_to_notify):
                print(f"title: {post.title}\nurl: {post.url}\n")
                self.pb.send_note(post.title, post.url)
            if posts_to_notify:
                self.last_post_time = posts_to_notify[-1].created_utc


def main():
    """
    The main function to run the RedditScanner.

    Initializes the RedditScanner with subreddit, regex, parameters, and flairs,
    then continuously scans for new posts every 10 minutes.
    """
    scanner = RedditScanner(
        subreddit="bapcsalescanada",  # Subreddit name
        regex=r"",  # Optional regex
        parameters=["nvme"],  # Mandatory parameters
        flairs=[]  # Optional flairs
    )

    while True:
        scanner.scan_new_posts()
        time.sleep(600)


if __name__ == '__main__':
    main()
