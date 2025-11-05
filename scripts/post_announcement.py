#!/usr/bin/env python3
"""Post announcement thread to Twitter."""

import os
import tweepy

def post_announcement():
    # Get credentials from environment
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # Thread of tweets
    tweets = [
        # Tweet 1: Main announcement
        """Introducing Eastbound Reports: an independent, open-source platform for Russian media analysis.

Our mission: Help English-speaking audiences understand Russian media narratives through accurate translation, context, and comparison with Western coverage.

https://petesumners.github.io/eastbound""",

        # Tweet 2: What makes us different
        """What makes Eastbound different:

✅ Completely independent (no government ties)
✅ 100% open source (GitHub)
✅ Transparent methodology
✅ Objective analysis without partisan bias
✅ AI-powered automation (with clear disclaimers)""",

        # Tweet 3: The tech
        """The tech stack:

• AI-generated content via Claude API
• Automated Russian media monitoring (RSS)
• Jekyll website on GitHub Pages
• Fully automated publishing pipeline
• All at ~$3/month

Everything runs in the cloud. Zero platform risk.""",

        # Tweet 4: Coming soon
        """Coming soon: Daily AI-generated analysis of Russian media coverage.

Each post will include:
• Multiple Russian source perspectives
• Context Western audiences miss
• Comparison with Western framing
• Clear AI-generated disclaimers

First post drops soon. Stay tuned. 🚀"""
    ]

    print("Posting announcement thread...")
    previous_id = None

    for i, tweet_text in enumerate(tweets, 1):
        try:
            if previous_id:
                response = client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=previous_id
                )
            else:
                response = client.create_tweet(text=tweet_text)

            tweet_id = response.data['id']
            previous_id = tweet_id

            print(f"Tweet {i}/{len(tweets)} posted: {tweet_id}")

        except Exception as e:
            print(f"Error posting tweet {i}: {e}")
            return False

    print("\nSUCCESS: Thread posted!")
    print(f"View at: https://twitter.com/EastboundReport/status/{tweets[0]}")

    return True

if __name__ == '__main__':
    success = post_announcement()
    exit(0 if success else 1)
