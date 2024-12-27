# Reddit Scanner with Pushbullet Notifications

This project scans specific subreddits for new posts that match given criteria and sends notifications with the post title and link to your devices using Pushbullet.


## Features

- Searches for new posts in specified subreddits.
- Filters posts based on specific criteria (Regex and/or parameters).
- Sends notifications with post title and link via Pushbullet.

## Setup

### Prerequisites

- Python 3.x
- Pushbullet account and API key
- Reddit `client_id`, `client_secret`, and `user_agent` for PRAW

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   ```

2. Navigate to the project directory and install the required packages:
   ```bash
   cd reddit-scanner
   pip install praw pushbullet.py
   ```

3. Set up your keys. Rename `keys_example.py` to `keys.py` and fill in the necessary API keys and Reddit credentials.

## Usage

Run the main script:
```bash
python main.py
```

The script will periodically scan the specified subreddit for new posts based on your criteria and send a Pushbullet notification for each match.

## Configuration

You can modify the following configurations in `main.py`:

- `subreddit`: Name of the subreddit to scan.
- `regex`: Regular expression to match against post titles.
- `parameters`: List of keywords to check in post titles.