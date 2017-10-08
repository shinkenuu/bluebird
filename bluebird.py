#!/usr/bin/env python
# encoding: utf-8


from datetime import datetime
import json
import tweepy  # https://github.com/tweepy/tweepy
import os


# Reads Twitter API credentials from .json
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'twitter_api_credentials.json')) as json_file:
    api_creds = json.load(json_file)

# Twitter only allows access to a user's latest 3240 tweets with this method
auth = tweepy.OAuthHandler(api_creds['consumer']['key'], api_creds['consumer']['secret'])
auth.set_access_token(api_creds['access']['key'], api_creds['access']['secret'])
api = tweepy.API(auth)


class Mention:
    def __init__(self, mentioned: str, when: datetime, mention_times: int=0):
        self.mentioned = mentioned
        self.when = when
        self.mention_times = mention_times

    def __str__(self):
        return ','.join([self.mentioned, self.when.strftime('%Y-%m-%d'), str(self.mention_times)])


def grab_tweets_with_mentions(screen_name: str):
    """
    Grabs data from tweeter and creates Tweet objects with the retrieved data
    :return: list of Tweets with mentions
    """
    tweets = []

    mention_num = 1
    for status in tweepy.Cursor(api.user_timeline, screen_name=screen_name).items(200):
        if len(status.entities['user_mentions']) < 1 or len(status.entities['hashtags']) < 1:
            continue  # ignore tweets without mentions or hash tags
        tweet = {
            'created_at': status.created_at,
            'screen_names': set([user_mention['screen_name'] for user_mention in status.entities['user_mentions']]),
            'hashtags': set([hashtag['text'] for hashtag in status.entities['hashtags']]),
        }
        tweets.append(tweet)
        print('{} tweet(s) grabbed'.format(mention_num))
        mention_num += 1
    return tweets


def init_mentions(tweets: list):
    """

    :param tweets:
    :return:
    """
    mentions = []

    for tweet in tweets:
        for screen_name in tweet['screen_names']:
            mentions.append(Mention(mentioned=screen_name, when=tweet['created_at']))
        for hashtag in tweet['hashtags']:
            mentions.append(Mention(mentioned=hashtag, when=tweet['created_at']))

    for mention_year_month in set([mention.when.date().replace(day=1) for mention in mentions]):
        mentions_within_same_month = [mention for mention in mentions
                                      if mention.when.date().replace(day=1) == mention_year_month]

        for mention in mentions_within_same_month:
            mention.mention_times = len([inner_mention for inner_mention in mentions_within_same_month
                                        if mention.mentioned == inner_mention.mentioned])

    return mentions


def create_file_with_mentions(mentions: list, path_to_file: str=os.path.expanduser('~'), file_name: str='tweets'):
    """
    Creates file with twitter data
    :return: the saved file path
    """
    file_path = '{}/{}.csv'.format(path_to_file, file_name)

    with open(file_path, 'w'):
        pass

    with open(file_path, 'w') as file:
        file.write('mentioned,when,times_same_month\n')
        for mention in mentions:
            file.write(str(mention) + '\n')

    return file_path


def record_mentions(screen_name: str, file_path: str=None):
    """

    :param screen_name:
    :param file_path:
    :return:
    """
    tweets = grab_tweets_with_mentions(screen_name=screen_name)
    mentions = init_mentions(tweets=tweets)
    if file_path is not None:
        return create_file_with_mentions(mentions=mentions,
                                         path_to_file=os.path.dirname(file_path),
                                         file_name=os.path.basename(file_path))
    return create_file_with_mentions(mentions=mentions)


if __name__ == '__main__':
    _screen_name = input(
        'Benvindo ao BlueBird! Insira o nome (com minúsculas e maiúsculas) da conta do twitter que deseja analizar:\n')
    _file_path = record_mentions(screen_name=_screen_name)
    print('Tweets saved at {}'.format(_file_path))
