from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import re
import requests
import eyed3
from requests_html import HTMLSession

API_KEY = 'PUT YOU YT API HERE'  # keep secret
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' \
             ' Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.49'
header = {'User-Agent': USER_AGENT}
youtube = build('youtube', 'v3', developerKey=API_KEY)


# Youtube
def youtube_get_info(link):
    try:  # ver como vai fazer pra suportar playlists
        response = get_id_response(link=link)
        song_info = dict()
        video_title = response['items'][0]['snippet']['title']
        video_date = response['items'][0]['snippet']['publishedAt']
        song_info.update({'youtube_title': video_title})
        song_info.update({'youtube_date': video_date})
        song_info.update({'youtube_year': re.search('^(\\d{4})-', video_date).group(1)})
        song_info.update({'youtube_month': re.search('-(\\d{2})-', video_date).group(1)})
        song_info.update({'youtube_day': re.search('-(\\d{2})T', video_date).group(1)})
        song_info.update({'link': link})
        return song_info
    except NameError:
        raise NameError('Link ou ID inválido.')
    except AttributeError:
        raise AttributeError('Música não encontrada no Genius')


def validate_id(response):
    if response['pageInfo']['totalResults'] > 0:
        return True
    else:
        raise NameError('Link ou ID inválido.')


def link_to_id(entry):
    link_id = re.search(
        pattern='(?:http|https|)(?:://|)(?:www.|)(?:youtu\.be/|youtube\.com(?:/embed/|/v/|/watch\?v=|/ytscreeningroom\?v=|/feeds/api/videos/|/user\S*[^\w\-\s]|\S*[^\w\-\s]))([\w\-]{11})[a-z0-9;:@#?&%=+/$_.-]*',
        string=entry)
    return link_id.group(1)


def test(search_string):
    response = youtube.search().list(part='snippet', q=search_string, type='video').execute()
    return response


def get_id_response(link):  # if has video and playlist then ask
    if re.search(pattern='youtu', string=link):
        if re.search(pattern='list=', string=link):
            link_id = re.search(pattern='(?:http|https|)(?:://|)(?:www.|)(?:youtu\.be/|youtube\.com(?:/embed/|/v/|/watch\?v=|/ytscreeningroom\?v=|/feeds/api/videos/|/user\S*[^\w\-\s]|\S*[^\w\-\s]))([\w\-]{12,})[a-z0-9;:@#?&%=+/$_.-]*', string=link)
            response = youtube.playlists().list(part='snippet', id=link_id.group(1)).execute()  # pode receber uma lista de IDs
        else:
            # link_id = re.search(pattern='(?:http|https|)(?:://|)(?:www.|)(?:youtu\.be/|youtube\.com(?:/embed/|/v/|/watch\?v=|/ytscreeningroom\?v=|/feeds/api/videos/|/user\S*[^\w\-\s]|\S*[^\w\-\s]))([\w\-]{11})[a-z0-9;:@#?&%=+/$_.-]*', string=link)
            response = youtube.videos().list(part='snippet', id=link_to_id(link)).execute()
            # print(response2)
        try:
            validate_id(response=response)
            return response
        except NameError:
            # return 'Link ou ID inválido.'
            raise NameError('Link ou ID inválido.')
    else:
        for link_type in (youtube.playlists, youtube.videos):
            try:
                response = link_type().list(part='snippet', id=link).execute()
                validate_id(response=response)
                return response
            except NameError:
                pass
        # return 'Link ou ID inválido.'
        raise NameError('Link ou ID inválido.')


# Genius
def genius_search(title):
    regex = '^\\d{1,2}| part.| feat.| ft.| prod.|\\(.*\\)|\\[.*\\]|\\{.*\\}|([^\\s\\w]|_)+'
    title_url = re.sub(' +', '+', re.sub(regex, '', title).strip())
    search_url = f'https://genius.com/api/search/multi?per_page=5&q={title_url}'
    request = requests.get(search_url)
    search_json = request.json()['response']['sections'][0]['hits']
    search_result = {}
    if len(search_json) > 0:
        print(search_json)
        for item in search_json:
            if item['type'] == 'song':
                search_result.update({item['result']['full_title'].replace('\xa0', ' '): item['result']['url']})
        return search_result
    else:
        return None


def genius_get_info(search_result):
    # search_result = genius_search(title=title).values()[1]
    if search_result is not None:
        request = requests.get(search_result, headers=header)
        html_soup = BeautifulSoup(request.text, 'html.parser')

        song_info = {'genius_title': '',
                     'genius_artist': '',
                     'genius_album': '',
                     'genius_album_art': '',
                     'genius_lyrics': '',
                     'genius_track': ''}

        if html_soup.findAll(attrs={'class': 'metadata_unit-info'}):
            classes = ['header_with_cover_art-primary_info-title',
                       'header_with_cover_art-primary_info-primary_artist',
                       'song_album-info-title',
                       'cover_art-image',
                       'track_listing-track track_listing-track--current',
                       'lyrics']
        else:
            classes = ['SongHeader__Title-sc-1b7aqpg-7 eJWiuG',
                       'Link-h3isu4-0 dpVWpH SongHeader__Artist-sc-1b7aqpg-9 eTAmkN',
                       'HeaderTracklist__Album-sc-1qmk74v-3 hxXYDz',
                       'SizedImage__NoScript-sc-1hyeaua-1 hYJUSb',
                       'AlbumTracklist__TrackName-sc-123giuo-2 guEaas',
                       'Lyrics__Container-sc-1ynbvzw-6 krDVEH']

        title = attribute(html_soup, classes[0])
        song_info['genius_title'] = title if title else attribute(html_soup, 'SongHeader__Title-sc-1b7aqpg-7 jQiTNQ')
        song_info['genius_artist'] = attribute(html_soup, classes[1])
        song_info['genius_album'] = attribute(html_soup, classes[2])

        genius_album_art = html_soup.find(attrs={'class': classes[3]})
        if genius_album_art:
            genius_album_art = genius_album_art['src']
            genius_album_art = re.sub('%2F', '/', genius_album_art)
            genius_album_art = re.search('images\\.genius\\.com/(.*)$', genius_album_art)
            if genius_album_art:
                song_info['genius_album_art'] = f'https://images.genius.com/{genius_album_art.group(1)}'
            else:
                song_info['genius_album_art'] = ''
        else:
            song_info['genius_album_art'] = ''

        genius_track = attribute(html_soup, classes[4])
        if genius_track != '':
            genius_track = re.search('\\d+', genius_track)
            song_info['genius_track'] = genius_track.group(0)
        else:
            song_info['genius_track'] = genius_track

        genius_lyrics = [lyrics for lyrics in html_soup.findAll(attrs={'class': classes[5]})]
        song_info['genius_lyrics'] = lyric_translate(genius_lyrics).strip()
    else:
        song_info = {'Não encontrado.'}
    return song_info


def lyric_translate(lyrics):
    if len(lyrics) > 1:
        lyrics = [re.sub(r'<div.*?>|<a.*?>|<span.*?>|</span>|</a>|<i>|</i>|</div>', '', str(i)) for i in lyrics]
        lyrics = ''.join(lyrics)
        lyrics = re.sub(r'<br/>', '\n', lyrics)
        lyrics = re.sub(r'<.*>', '\n', lyrics)
    else:
        lyrics = re.sub(r'<br/>', '\n', str(lyrics[0]).strip())
        lyrics = re.sub(r'<.*?>', '', lyrics)
        lyrics = re.sub(r'<a[^<]+>', '', lyrics)
        lyrics = re.sub(r'[\r\n]{1,2}', '\n', lyrics)
    return lyrics


def attribute(html, cl):
    if html.find(attrs={'class': cl}):
        info = html.find(attrs={'class': cl}).text
        return info.strip()
    else:
        return ''


# eyeD3
def set_properties(song_info, song_path, song_cover):
    # audio.initTag() wipe tag info
    a_file = eyed3.load(song_path)
    a_file.tag.artist = song_info['genius_artist']
    a_file.tag.title = song_info['genius_title']
    if song_info['genius_artist'] != '':
        a_file.tag.album_artist = song_info['genius_artist']
    if song_info['genius_album'] != '':
        a_file.tag.album = song_info['genius_album']
    if song_info['genius_track'] != '':
        a_file.tag.track_num = song_info['genius_track']
    # a_file.tag.genre = song_info['genius_track']
    a_file.tag.release_date = int(re.search(r'/../(.+)$', song_info['date']).group(1))
    if song_cover != '':
        print(song_cover)
        print(song_info['genius_album_art'])
        a_file.tag.images.set(3, song_cover, 'image/jpeg', 'album_arte')
                              # img_url=song_cover)
    a_file.tag.save()
