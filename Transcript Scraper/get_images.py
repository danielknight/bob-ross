from bs4 import BeautifulSoup
import os
import urllib.request

dir = os.path.dirname(__file__)


def find_season(season_num):
    directory = os.path.join(dir, 'Transcripts', 'The Joy of Painting - Season %s' % season_num)
    return directory

def get_images():
    episode_pics = {}
    with open('1209k_data.html',) as infile:
        html = infile.read()
        soup = BeautifulSoup(html, "html.parser")
        titles = [h4.get_text().split() for h4 in soup.find_all("h4")]
        print(titles)
        src = [''.join(['https://1209k.com/bobross/', img['src']]) for img in soup.find_all('img')]
        print(src)

        for title, link in zip(titles, src):
            #get dest directory based on title season and episode
            season = title[0]
            epi_num = title[2]
            directory = find_season(season)
            print(directory)
            for root, dirs, files in os.walk(directory):
                for dirname in dirs:
                    if 'Episode %s)' % epi_num in dirname:
                        #we found the season and episode dir, download and write to file
                        if not os.path.exists('painting%s-%s.jpg' % (season, epi_num)):
                            urllib.request.urlretrieve(link,
                                                   os.path.join(root, dirname, 'painting%s-%s.jpg' % (season, epi_num)))
                            print("SUCCESS")
                    else:
                        print("no episode found in %s" % dirname)
    return 0

get_images()

