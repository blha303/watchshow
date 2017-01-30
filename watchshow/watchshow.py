#!/usr/bin/env python3
from requests import get
from bs4 import BeautifulSoup as Soup
from base64 import b64decode
from json import loads
from argparse import ArgumentParser
from sys import exit, stderr

def get_ep_info_url(show, season, episode):
    show = "-".join(show.lower().split(" "))
    page = Soup(get("http://putlockers.ch/watch-{}-tvshow-online-free-putlocker.html".format(show)).text, "html.parser")
    seasons = [a.text.split()[-1] for a in page.findAll("a", {"class": "selector_name"})]
    if season in seasons:
        table = [table for table in page.findAll("table", {"class": "table"})][:-3][seasons.index(season)]
        eps = {a.text.split()[-1]:a["href"] for a in table.findAll("a")}
        if episode in eps:
            return eps[episode]

def get_video_urls(page_url):
    page = get(page_url).text
    iframe_b64 = page.split("""<script type="text/javascript">document.write(doit('""")[2].split("'")[0]
    iframe = Soup(b64decode(b64decode(iframe_b64)), "html.parser")
    video_page = get(iframe.iframe["src"]).text
    sources = video_page.split("sources: ")[1].split(",\n")[0]
    return loads(sources.replace('{file:', '{"file":').replace(',label:', ',"label":'))

def main():
    parser = ArgumentParser(prog="watchshow")
    parser.add_argument("show", help="Name of show to get")
    parser.add_argument("season", help="Season number")
    parser.add_argument("episode", help="Episode number")
    args = parser.parse_args()
    page_url = get_ep_info_url(args.show, args.season, args.episode)
    if not page_url:
        print("Season/episode not found", file=stderr)
        return 1
    sources = get_video_urls(page_url)
    print(sources[-1]["file"])
    return 0

if __name__ == "__main__":
    exit(main())
