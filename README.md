# youmusic
A simple python program that transfer your csv music playlist to YouTube

### Dependence

```python
argparse
configparser
googleapiclient
oauth2client
```

### Usage

#### Step 1

Go to google api https://console.developers.google.com, creat a new project or use your existing project. Select your project and then click Enable Apis And Services: 

![Enable APIS](https://cdn.jsdelivr.net/gh/viewv/Pico/img/20200124124250.png)

and then search YouTube, enable YouTube Data API v3

![Youtube API](https://cdn.jsdelivr.net/gh/viewv/Pico/img/20200124124402.png)

Here I already enable it, and then you need to creat your credentials.

#### Step 2

![creat credentials](https://cdn.jsdelivr.net/gh/viewv/Pico/img/20200124124635.png)

Click Credentials.

![API](https://cdn.jsdelivr.net/gh/viewv/Pico/img/20200124124756.png)

First you need to create a API key (I call this API key). Second you need create a OAuth client ID.

![OAuth client ID](https://cdn.jsdelivr.net/gh/viewv/Pico/img/20200124124923.png)

choose Other, google may need you to create a OAuth consent screen, just set one, that can work without Google's Verification.

After you create your OAuth client ID, you can download you OAuth client ID json file, rename into client.json and place under this program folder.

#### Step 3

You need to config some lines in this program.

First open settings.cfg file, its should look like this:

```

# This is an example configuration file for the Create Billboard Charts
# YouTube Playlists script. Copy this file to settings.cfg and edit it to
# include your Google API info.

[accounts]
# The API Key for your Google API project
# If you don't have a Google API project already, you can create one in
# the Google Developer Console:
# https://console.developers.google.com/
# The default key is not valid, but looks similar to a valid key
api_key = AIzaSyDsSa9Ac88dYQIhyQZQc-s63My_E_Z1b5k
```

change api_key with your api key.

Second goto main.py find code below:

```python
# INFO
# Your API key
DEVELOPER_KEY = 'AIzaSyDsSa9Ac88dYQIhyQZ'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
```

change `DEVELOPER_KEY` into your api key

#### Step 4

Now you need playlist csv, you can go to https://www.tunemymusic.com, and export your playlist in csv format. Rename into `list.csv` , then place below program folder.

After all steps, you can run main.py but in fact you need change some code.

#### Config

- First:

    ```python
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
    ```

    In this part you can change max_results, defalut 1 means one name get one video, 2 means one name get max two videos ... 

- Second:

    ```python
    #! Set a suitable Amount
    allvideos = getAllMusic(df['Track name'][:1])
    ```

    Defalut set 1 ([:1]), really small, means just search your first song or your list and add into your list.

    you can change into a bigger one, but remember, google limit your api usage, if you set too big, may be you will run out of your limitation, I test for this program, mey be you can set 50 songs for one time, that means you can first run at `[:50]`, second `[50:100]`  and so on.

Now you can run this code by `python main.py`

### Info

This tiny tiny ... project is now for my own usage, code is mainly get from [aag](https://github.com/aag)/**[billboard_yt_playlist_creator](https://github.com/aag/billboard_yt_playlist_creator)**  . Thank you very much, the part I added is really small, really ugly, really sorry for that.

## Thanks

[aag](https://github.com/aag)/**[billboard_yt_playlist_creator](https://github.com/aag/billboard_yt_playlist_creator)**