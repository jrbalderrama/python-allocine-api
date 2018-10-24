from base64 import b64encode
from collections import defaultdict
from datetime import date, datetime
from urllib.parse import urlencode
import hashlib
import json
import time
import sys

import requests


ALLOCINE_BASE_URL = "http://api.allocine.fr/rest/v3/"
ALLOCINE_PARTNER_KEY = '100043982026'
ALLOCINE_SECRET_KEY = '29d185d98c984a359e6e6f26a0474269'
ANDROID_USER_AGENT = 'Dalvik/1.6.0 (Linux; U; Android 4.2.2; Nexus 4 Build/JDQ39E)'


def do_request(method, params):
    sed = time.strftime("%Y%m%d")
    sha1 = hashlib.sha1()
    PARAMETER_STRING = "partner=" + ALLOCINE_PARTNER_KEY + "&" + "&".join([k + "=" + params[k] for k in params.keys()]) + "&sed=" + sed
    SIG_STRING = bytes(ALLOCINE_SECRET_KEY + PARAMETER_STRING, 'utf-8')
    sha1.update(SIG_STRING)
    SIG_SHA1 = sha1.digest()
    SIG_B64 = b64encode(SIG_SHA1).decode('utf-8')
    sig = urlencode({SIG_B64: ''})[:-1]
    URL = ALLOCINE_BASE_URL + method + "?" + PARAMETER_STRING + "&sig=" + sig
    headers = {'User-Agent': ANDROID_USER_AGENT}
    results = requests.get(URL, headers=headers).text
    try:
        return json.loads(results)
    except Exception as e:
        return results


# search :
#   q : string to search
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   filter (optionnal) : filter depending on the result type ("movie", "theater", "person", "news", "tvseries", separated by a comma)
#   count (optionnal) : number of results to return (should be an integer)
#   page (optionnal) : number of the results page to return (default is 10 results by page)
def search(string, format="json", filter=None, count=None, page=None):
    data = {'q': str(string), 'format': str(format)}
    if filter is not None:
        data["filter"] = filter.replace(",", "%2C")
    if count is not None:
        data["count"] = str(count)
    if page is not None:
        data["page"] = str(page)
    return do_request("search", data)


# movie : information about a movie
#   code : film id (should be an integer)
#   profile (optionnal) : level of information returned ("small", "medium", or "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2")
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   filter (optionnal) : filter depending on the result type ("movie", "theater", "person", "news", "tvseries", separated by a comma)
#   striptags (optionnal) : remove the HTML tags from the value returned ("synopsis", "synopsisshort", separated by a comma)
def movie(code, profile=None, mediafmt=None, format="json", filter=None, striptags=None):
    data = {'code': str(code), 'format': format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    data['format'] = format
    if filter is not None:
        data["filter"] = filter
    if striptags is not None:
        data["striptags"] = striptags
    return do_request("movie", data)


# reviewlist : critic (public or press) about a movie
#   type : type ("movie")
#   code : film id (should be an integer)
#   filter : critic type ("public", "desk-press")
#   count (optionnal) : number of critic to return (should be an integer)
#   page (optionnal) : page number to return (10 results by page by default)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def reviewlist(code, filter="public%2Cdesk-press", count=None, page=None, format="json"):
    data = {'code': str(code), "filter": filter, "format": format}
    if count is not None:
        data["count"] = str(count)
    if page is not None:
        data["page"] = str(page)
    return do_request("reviewlist", data)


# showtimelist : theater schedule
#   zip : postal code of the city
#   lat : latitude coordinate of the theater
#   long : longitude coordinate of the theater
#   radius : radius around the location (between 1 and 500 km)
#   theaters : theaters code list (separated by a comma)
#   location : string identifying the theater
#   movie (optionnal) : film id (should be an integer, if not set, returns all movies)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   date (optionnal) : date, in the YYYY-MM-DD format (if not set, set to today)
def showtimelist(zip=None, lat=None, long=None, radius=None, theaters=None, location=None, movie=None, format="json", date=None):
    data = {"format": format}
    if zip is not None:
        data["zip"] = str(zip)
    if lat is not None:
        data["lat"] = str(lat)
    if long is not None:
        data["long"] = str(long)
    if radius is not None:
        data["radius"] = str(radius)
    if theaters is not None:
        data["theaters"] = theaters.replace(",", "%2C")
    if location is not None:
        data["location"] = location
    if movie is not None:
        data["movie"] = str(movie)
    if date is not None:
        data["date"] = date
    return do_request("showtimelist", data)


# media : information about a media
#   code : media id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def media(code, profile=None, mediafmt=None, format="json"):
    data = {"code": code, "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    return do_request("media", data)


# person : information about a person
#   code : person id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   filter (optionnal) : filter results by type ("movie", "theater", "person", "news", "tvseries", separated by a comma)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def person(code, profile=None, mediafmt=None, filter=None, format="json"):
    data = {"code": code, "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    if filter is not None:
        data["filter"] = filter
    return do_request("person", data)


# filmography : person filmography
#   code : person id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   filter (optionnal) : filter the results by type ("movie", "theater", "person", "news", "tvseries", separated by a comma)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def filmography(code, profile=None, filter=None, format="json"):
    data = {"code": code, "format": format}
    if profile is not None:
        data["profile"] = profile
    if filter is not None:
        data["filter"] = filter
    return do_request("filmography", data)


# movielist : movie list in theater
#   code : person id (should be an integer)
#   count (optionnal) : number of results to return (should be an integer)
#   page (optionnal) : number of the results page to return (default is 10 results by page)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   filter (optionnal) : filter results by type ("nowshowing", "comingsoon", separated by a comma)
#   order (optionnal) : order to sort the results ("datedesc", "dateasc", "theatercount", "toprank")
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def movielist(code, count=None, page=None, profile=None, filter=None, order=None, format="json"):
    data = {"code": str(code), "format": format}
    if count is not None:
        data["count"] = str(count)
    if page is not None:
        data["page"] = page
    if profile is not None:
        data["profile"] = profile
    if filter is not None:
        data["filter"] = filter
    if order is not None:
        data["order"] = order
    return do_request("movielist", data)


# theaterlist : theater list
#   zip : postal code of the city
#   lat : latitude coordinate of the theater
#   long : longitude coordinate of the theater
#   radius : radius around the location (between 1 and 500 km)
#   theater : theater code (should be an integer)
#   location : string identifying the theater
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def theaterlist(zip=None, lat=None, long=None, radius=None, theater=None, location=None, format="json"):
    data = {"format": format}
    if zip is not None:
        data["zip"] = str(zip)
    if lat is not None:
        data["lat"] = str(lat)
    if long is not None:
        data["long"] = str(long)
    if radius is not None:
        data["radius"] = str(radius)
    if theater is not None:
        data["theater"] = theater
    if location is not None:
        data["location"] = location
    return do_request("theaterlist", data)


# tvseries : information about a TV serie
#   code : serie id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   striptags (optionnal) : remove the HTML tags from the value returned ("synopsis", "synopsisshort", separated by a comma)
def tvseries(code, profile=None, mediafmt=None, format="json", striptags=None):
    data = {"code": str(code), "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    if striptags is not None:
        data["striptags"] = striptags
    return do_request("tvseries", data)


# season : information about a TV serie season
#   code : season id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   striptags (optionnal) : remove the HTML tags from the value returned ("synopsis", "synopsisshort", separated by a comma)
def season(code, profile=None, mediafmt=None, format="json", striptags=None):
    data = {"code": str(code), "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    if striptags is not None:
        data["striptags"] = striptags
    return do_request("season", data)


# episode : information about an episode
#   code : season id (should be an integer)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   mediafmt (optionnal) : video format ("flv", "mp4-lc", "mp4-hip", "mp4-archive", "mpeg2-theater", "mpeg2", ...)
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
#   striptags (optionnal) : remove the HTML tags from the value returned ("synopsis", "synopsisshort", separated by a comma)
def episode(code, profile=None, mediafmt=None, format="json", striptags=None):
    data = {"code": str(code), "format": format}
    if profile is not None:
        data["profile"] = profile
    if mediafmt is not None:
        data["mediafmt"] = mediafmt
    if striptags is not None:
        data["striptags"] = striptags
    return do_request("episode", data)


def map_lang(code):
    languages = {
        6001: 'français',
        6002: 'English',
        6003: 'español',
        6004: "italiano",
        6006: 'deutsch',
        6008: 'Chinese',
        6009: 'Hindi',
        6011: 'Arab',
        6015: 'Danish',
        6019: 'Hebrew',
        6021: 'Japanese',
        6027: 'Portuguese',
        6026: 'Polish',
        6030: 'Russian', #to confirm
        6033: 'Swedish',
        6036: 'Turkish',
        6040: 'Korean',
        6053: 'Icelandic',
        6055: 'Finnish',
        6104: 'Ukrainian'
    }
    return languages.get(code, code)


MY_LANGS = [6002, 6003, 6004, 6006]


def map_theatre(cinema):
    theatre = {
        'arvor': 'P0084',
        'cineville': 'P0085',
        'colombier': 'P0085',
        'tnb': 'P0102',
        'gaumont': 'P0091'}
    return theatre.get(cinema, cinema)


def to_str(runtime):
    total_seconds: int = int(runtime)
    hours: int = total_seconds // 3600
    minutes: int = total_seconds // 60 % 60
    seconds: int = total_seconds % 60
    return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)


def week_planning(planning):
    schedule = defaultdict(list)
    for week_day in planning:
        day_ = week_day['d']
        for slot in week_day['t']:
            schedule[day_].append(slot['$'])
    return schedule


def today_planning(planning):
    today_hours = [hours for day, hours in week_planning(planning).items()
                   if day == date.today().isoformat()][0]
    current_hour = datetime.now().hour
    return [hour for hour in today_hours
            if datetime.strptime(hour, '%H:%M').hour > current_hour]


def lookup_original_name(code):
    return movie(code, filter='movie')['movie']['originalTitle']


def to_stars(rating):
    stars = int(rating) % 5 + (1 if int(rating * 100) % 100 >= 51  else 0)
    return ''.join(['☆' for x in range(stars)])



if __name__ == "__main__":
    theatre = map_theatre(sys.argv[1])
    #theatre = 'P0787' #'C0100'
    show_week = len(sys.argv) > 2
    my_date = None if show_week else date.today().isoformat()
    movie_list = showtimelist(theaters=theatre, date=my_date) \
        ['feed']['theaterShowtimes'][0]['movieShowtimes']
    for my_movie in movie_list:
        release = my_movie['releaseWeek']
        week_release = '·' if release == 'true' else '×'
        language = my_movie['version']['lang']
        planning = my_movie['scr']
        information = my_movie['onShow']['movie']
        code = information['code']
        title = information['title']
        genre = information['genre'][0]['$']
        live = True if 'Pathé' in title else False
        directors = information.get('castingShort', {})
        directors = directors.get('directors', '')
        runtime = information.get('runtime', 0)
        rating = information['statistics'].get('pressRating', 0)
        fans = information['statistics'].get('userRating', 0)
        trailer = information['link'][0]['href']
        if not live:
            if language in MY_LANGS:
                title = lookup_original_name(code)

            rating_constellation = to_stars(rating)
            fans_constellation = to_stars(fans)
            separator = '|' \
                if rating_constellation and fans_constellation else ''
            print('{} {}, {} ({}) {}{}{}'.format(
                week_release,
                title,
                genre,
                map_lang(language),
                '{}'.format(rating_constellation),
                separator,
                '{}'.format(fans_constellation)))
            if show_week:
                for day, hours in week_planning(planning).items():
                    week_day = datetime.strptime(day, '%Y-%m-%d').date()
                    print('\t\t{}: {}'.format(week_day.strftime('%A %b, %d'),
                                              ', '.join(hours)))

            else:
                planning = today_planning(planning)
                if planning:
                    print('\t\t{}'.format(', '.join(planning)))

        # TODO async for foreing movies
