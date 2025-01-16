import time
import csv
import requests
from bs4 import BeautifulSoup


class Extractor_Lyrics:

    def __init__(self):
        Lucy_url = "https://music.bugs.co.kr/artist/80332208/tracks?type=RELEASE"
        response = requests.get(
            Lucy_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            },
        )
        self.soup = BeautifulSoup(response.content, "html.parser")

    def start_crawling(self):
        track_urls = self.track_url_crawling()
        album_data = self.find_release_date()
        lyrics = self.lyrics_scrapping(track_urls, album_data)
        self.save_to_file("Lucy", lyrics)

    def wait(self, seconds=4):
        time.sleep(seconds)

    def track_url_crawling(self):
        paging = len(self.soup.find("div", class_="paging").find_all("a"))
        track_hrefs = []
        for i in range(paging):
            lyrics_url = f"https://music.bugs.co.kr/artist/80332208/tracks?type=RELEASE&sort=P&page={i+1}&roleCode=0&highQualityOnly="
            response = requests.get(
                lyrics_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")
            songs = soup.find_all("tr", artistid="80332208")
            for song in songs:
                track_href = song.find("a", class_="trackInfo")["href"]
                track_hrefs.append(track_href)
        return track_hrefs

    def lyrics_scrapping(self, urls, album_data):
        lyrics_info = []
        for url in urls:
            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")

            title = soup.find("header", class_="pgTitle").find("h1").text
            if "Inst" in title or "inst" in title:
                continue
            lyric = soup.find("xmp")
            lyric = "곡 정보 없음" if not lyric else lyric.text
            album = (
                soup.find("div", class_="basicInfo").find_all("tr")[2].find("a").text
            )
            like = soup.find("a", class_="like").find("em").text

            release_date = album_data[album]

            lyrics_info.append(
                {
                    "title": title,
                    "lyric": lyric,
                    "album": album,
                    "like": like,
                    "release_date": release_date,
                }
            )
        return lyrics_info

    def find_release_date(self):
        types = ["RELEASE", "JOIN", "COMPIL"]
        album_data = {}
        for type in types:
            url = f"https://music.bugs.co.kr/artist/80332208/albums?type={type}"
            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                },
            )
            soup = BeautifulSoup(response.content, "html.parser")

            albums = soup.find("ul", class_="albumList").find_all("li")

            for album in albums:
                album_title = album.find("div", class_="albumTitle").find("a").text
                album_release_date = album.find("time").text
                album_data[album_title] = album_release_date

        return album_data

    def save_to_file(self, file_name, lyrics):
        file = open(f"{file_name}.csv", "w", encoding="utf-8", newline="")
        writer = csv.writer(file)
        writer.writerow(["title", "lyric", "album", "like", "release_date"])

        for lyric in lyrics:
            writer.writerow(lyric.values())

        file.close()
