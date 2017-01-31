#!/usr/bin/env python3
from requests import get
from bs4 import BeautifulSoup as Soup
from base64 import b64decode
from json import loads
from argparse import ArgumentParser
from sys import exit, stderr
from collections import OrderedDict
from os.path import join as os_join

def get_ep_info(show):
    show = "-".join(show.lower().split(" "))
    page = Soup(get("http://putlockers.ch/watch-{}-tvshow-online-free-putlocker.html".format(show)).text, "html.parser")
    seasons = [a.text.split()[-1] for a in page.findAll("a", {"class": "selector_name"})]
    episode_tables = [table for table in page.findAll("table", {"class": "table"})][:-3]
    eps = OrderedDict()
    for i, s in enumerate(seasons):
        eps[s] = OrderedDict()
        for a in episode_tables[i].findAll("a"):
            eps[s][a.text.split()[-1]] = a["href"]
    return eps

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

def download(url, filename):
    req = get(url, stream=True)
    total = int(req.headers.get("Content-Length"))
    with open(filename, "wb") as f:
        progress = 0
        for chunk in req.iter_content(1024):
            if chunk:
                f.write(chunk)
                f.flush()
                progress += len(chunk)
                print("\r{}: {:3.1f}% ({}/{})     ".format(filename, progress / total * 100, progress, total), end="")

def main():
    parser = ArgumentParser(prog="watchshow")
    parser.add_argument("show", help="Show name")
    parser.add_argument("season", help="Season number", nargs="?")
    parser.add_argument("episode", help="Episode number", nargs="?")
    parser.add_argument("--dl", help="Download episode", action="store_true")
    parser.add_argument("--directory", help="Target directory for download", default=".")
    args = parser.parse_args()
    if not args.show:
        parser.print_help()
        return 1
    eps = get_ep_info(args.show)
    if not args.episode:
        for season,episodes in eps.items():
            if args.season and args.season != season:
                continue
            for episode,url in episodes.items():
                try:
                    vid_url = get_video_urls(url)[-1]["file"]
                    if args.dl:
                        download(vid_url, os_join(args.directory, "{} S{}E{}.mp4".format(args.show, season.zfill(2), episode.zfill(2))))
                    else:
                        print(vid_url)
                except (KeyError, IndexError):
                    print("No video found for s{}e{}".format(season.zfill(2), episode.zfill(2)), file=stderr)
    elif args.season in eps:
        if args.episode in eps[args.season]:
            sources = get_video_urls(eps[args.season][args.episode])
            if not sources:
                print("No video found", file=stderr)
                return 2
            if args.dl:
                download(sources[-1]["file"], os_join(args.directory, "{} S{}E{}.mp4".format(args.show, args.season.zfill(2), args.episode.zfill(2))))
            else:
                print(sources[-1]["file"])
        else:
            print("Episode not found", file=stderr)
            return 2
    else:
        print("Season not found", file=stderr)
        return 2
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("Aborted", file=stderr)
        exit(130)
