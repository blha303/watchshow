#!/usr/bin/env python3
from requests import get
from bs4 import BeautifulSoup as Soup
from base64 import b64decode
from json import loads
from argparse import ArgumentParser
from sys import exit, stderr, argv
from collections import OrderedDict

def get_ep_info_url(show, season="1", episode="1", bulk=False):
    show = "-".join(show.lower().split(" "))
    page = Soup(get("http://putlockers.ch/watch-{}-tvshow-online-free-putlocker.html".format(show)).text, "html.parser")
    seasons = [a.text.split()[-1] for a in page.findAll("a", {"class": "selector_name"})]
    episode_tables = [table for table in page.findAll("table", {"class": "table"})][:-3]
    eps = OrderedDict()
    for i, s in enumerate(seasons):
        eps[s] = OrderedDict()
        for a in episode_tables[i].findAll("a"):
            eps[s][a.text.split()[-1]] = a["href"]
    if bulk:
        return eps
    if season in eps:
        if episode in eps[season]:
            return eps[episode]

def get_video_urls(page_url):
    page = get(page_url).text
    try:
        iframe_b64 = page.split("""<script type="text/javascript">document.write(doit('""")[2].split("'")[0]
    except IndexError:
        return []
    iframe = Soup(b64decode(b64decode(iframe_b64)), "html.parser")
    video_page = get(iframe.iframe["src"]).text
    sources = video_page.split("sources: ")[1].split(",\n")[0]
    return loads(sources.replace('{file:', '{"file":').replace(',label:', ',"label":'))

def main():
    parser = ArgumentParser(prog="watchshow")
    parser.add_argument("show", help="Name of show to get")
    if "-b" not in argv:
        parser.add_argument("season", help="Season number")
        parser.add_argument("episode", help="Episode number")
    else:
        parser.add_argument("-b", "--bulk", help="Return bulk episode urls", action="store_true")
    args = parser.parse_args()
    if "bulk" in args:
        eps = get_ep_info_url(args.show, bulk=True)
        for season,episodes in eps.items():
            for episode,url in episodes.items():
                print("{} {}: ".format(season, episode), file=stderr)
                try:
                    vid_url = get_video_urls(url)[-1]["file"]
                    print(vid_url)
                except (KeyError, IndexError):
                    pass
                except KeyboardInterrupt:
                    print("Aborted", file=stderr)
                    return 130
        return 0
    page_url = get_ep_info_url(args.show, args.season, args.episode)
    if not page_url:
        print("Season/episode not found", file=stderr)
        return 1
    sources = get_video_urls(page_url)
    if not sources:
        print("No video found", file=stderr)
        return 2
    print(sources[-1]["file"])
    return 0

if __name__ == "__main__":
    exit(main())
