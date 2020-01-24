import time
import socks
import socket
import logging
import os.path
import httplib2
import argparse
from configparser import SafeConfigParser
from datetime import datetime

# Data
import pandas as pd

# Google Data API
from googleapiclient.discovery import build
import oauth2client
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow

# INFO
# Your API key
DEVELOPER_KEY = 'AIzaSyDsSa9Ac88dYQIhyQZ'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


class YoutubeAdapter(object):
    """An adapter class for the Youtube service. This class presents the API
    that our script logic needs and handles the interaction with the Youtube
    servers."""
    YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

    def __init__(self, logger, api_key, config_path):
        """Create an object which contains an instance of the YouTube service
        from the Google Data API library"""
        self.logger = logger

        client_secrets_file = config_path + "client.json"
        missing_secrets_message = "Error: {0} is missing".format(
            client_secrets_file
        )

        # Do OAuth2 authentication
        flow = flow_from_clientsecrets(
            client_secrets_file,
            message=missing_secrets_message,
            scope=YoutubeAdapter.YOUTUBE_READ_WRITE_SCOPE,
            redirect_uri=YoutubeAdapter.REDIRECT_URI
        )

        storage = Storage(config_path + "oauth.json")
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            parser = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                parents=[oauth2client.tools.argparser],
            )
            flags = parser.parse_args()

            credentials = run_flow(flow, storage, flags)

        # Create the service to use throughout the script
        self.service = build(
            YoutubeAdapter.YOUTUBE_API_SERVICE_NAME,
            YoutubeAdapter.YOUTUBE_API_VERSION,
            developerKey=api_key,
            http=credentials.authorize(httplib2.Http())
        )

    def get_video_id_for_search(self, query):
        """Returns the videoId of the first search result if at least one video
           was found by searching for the given query, otherwise returns
           None"""

        search_response = self.service.search().list(
            q=query,
            part="id",
            maxResults=3,
            safeSearch="none",
            type="video",
            fields="items"
        ).execute()

        items = search_response.get('items', [])
        if not items:
            return None

        for item in items:
            # The "type" parameter doesn't always work for some reason, so we
            # have to check each item for its type.
            if item['id']['kind'] == 'youtube#video':
                return item['id']['videoId']
            else:
                self.logger.warning(
                    "\tResult is not a video, continuing to next result"
                )

        return None

    def add_video_to_playlist(self, pl_id, video_id):
        """Adds the given video as the last video as the last one in the given
        playlist"""
        self.logger.info("\tAdding video pl_id: %s video_id: %s", pl_id,
                         video_id)

        video_insert_response = self.service.playlistItems().insert(
            part="snippet",
            body=dict(
                snippet=dict(
                    playlistId=pl_id,
                    resourceId=dict(
                        kind="youtube#video",
                        videoId=video_id
                    )
                )
            ),
            fields="snippet"
        ).execute()

        title = video_insert_response['snippet']['title']

        self.logger.info('\tVideo added: %s', title.encode('utf-8'))

    def create_new_playlist(self, title, description):
        """Creates a new, empty YouTube playlist with the given title and
        description"""
        playlists_insert_response = self.service.playlists().insert(
            part="snippet,status",
            body=dict(
                snippet=dict(
                    title=title,
                    description=description
                ),
                status=dict(
                    privacyStatus="public"
                )
            ),
            fields="id"
        ).execute()

        pl_id = playlists_insert_response['id']
        pl_url = self._playlist_url_from_id(pl_id)

        self.logger.info("New playlist added: %s", title)
        self.logger.info("\tID: %s", pl_id)
        self.logger.info("\tURL: %s", pl_url)

        return pl_id

    def playlist_exists_with_title(self, title):
        """Returns true if there is already a playlist in the channel with the
        given name"""
        playlists = self.service.playlists().list(
            part="snippet",
            mine=True,
            maxResults=10,
            fields="items"
        ).execute()

        for playlist in playlists['items']:
            if playlist['snippet']['title'] == title:
                return True

        return False

    @staticmethod
    def _playlist_url_from_id(pl_id):
        """Returns the URL of a playlist, given its ID"""
        return "https://www.youtube.com/playlist?list={0}".format(pl_id)


def load_config(logger):
    """Loads config values from the settings.cfg file in the script dir"""
    config_path = get_script_dir() + 'settings.cfg'
    section_name = 'accounts'

    if not os.path.exists(config_path):
        logger.error("Error: No config file found. Copy settings-example.cfg "
                     "to settings.cfg and customize it.")
        exit()

    config = SafeConfigParser()
    config.read(config_path)

    # Do basic checks on the config file
    if not config.has_section(section_name):
        logger.error("Error: The config file doesn't have an accounts "
                     "section. Check the config file format.")
        exit()

    if not config.has_option(section_name, 'api_key'):
        logger.error("Error: No developer key found in the config file. "
                     "Check the config file values.")
        exit()

    config_values = {
        'api_key': config.get(section_name, 'api_key'),
    }

    return config_values


def youtube_music_search(options, youtube):
    # Call the search.list method to retrieve results matching the specified
    # query term.

    search_response = youtube.search().list(
        q=options['q'],
        part='id',
        maxResults=options['max_results'],
        type='video',
        videoCategoryId="10"
    ).execute()

    channels = []
    playlists = []
    idresult = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            idresult.append(search_result['id']['videoId'])

    return idresult


def getAllMusic(tracks):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    result = []
    failtracks = []
    for track in tracks:
        print(track)
        try:
            #! You can change 'max_results': 1 into 2 or 3
            args = {'q': track, 'max_results': 1}
            res = youtube_music_search(args, youtube)
            result += res
        except Exception as e:
            failtracks.append(track)
    return {"ID": result, "Fail": failtracks}


def get_script_dir():
    """Returns the absolute path to the script directory"""
    return os.path.dirname(os.path.realpath(__file__)) + '/'


def main():
    """Script main function"""
    logging.basicConfig(format='%(message)s')
    logger = logging.getLogger('createbillboardplaylist')
    logger.setLevel(logging.INFO)

    config = load_config(logger)
    youtube = YoutubeAdapter(logger, config['api_key'], get_script_dir())

    print('start')

    #! read csv and search for song
    df = pd.read_csv('list.csv')
    
    #! Set a suitable Amount
    allvideos = getAllMusic(df['Track name'][:1])

    videos = allvideos['ID']
    failed = allvideos['Fail']

    print("ALL video")
    for video in videos:
        print(video)

    plname = input('Please input your new target playlist')

    pldescription = input('Please description of your new playlist')

    plist = youtube.create_new_playlist(plname, pldescription)

    for video in videos:
        youtube.add_video_to_playlist(plist, video)

    print("All Done")
    print("Failed Tracks")
    for track in failed:
        print(track)


if __name__ == "__main__":
    main()
