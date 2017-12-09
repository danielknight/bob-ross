import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os

playlistDir = 'https://www.youtube.com/user/BobRossInc/playlists?sort=dd&view=1&flow=list'


def getPlaylistUrls(playlistDirectory):
    # locate all the <a href=...link...> tags in the dir, add to list
    urlDict = {}
    driver = webdriver.Chrome()
    driver.get(playlistDirectory)
    time.sleep(1)
    try:
        '''playlistLinks = WebDriverWait(driver, 5).until(
            EC.visibility_of_all_elements_located((By.TAG_NAME, 'a')))'''
        playlistLinks = driver.find_elements_by_tag_name('a')
        print(len(playlistLinks))
        for playlistLink in playlistLinks:
            if 'View full playlist' in playlistLink.text:
                playlistTitle = playlistLink.find_element_by_xpath('.//../preceding-sibling::h3/a')
                urlDict[playlistTitle.text] = playlistLink.get_attribute('href')
    finally:
        for k, v in urlDict.items():
            print(k, v)
        driver.close()
    return urlDict


def getEpisodeUrls(seasonUrlDict):
    '''take a big dict of season urls and return a big dict of dicts '''
    episodesBySeason = {}
    driver = webdriver.Chrome()
    for k, v in seasonUrlDict.items():
        driver.get(v)  # open up the season playlist
        time.sleep(.5)
        seasonEpisodes = {}
        aTags = WebDriverWait(driver, 4).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, 'pl-video-title-link'))
                )
        for elem in aTags:
            seasonEpisodes[elem.text] = elem.get_attribute('href')
        # map(lambda elem: seasonEpisodes.update({elem.text: elem.get_attribute('href')}), aTags)
        # print(seasonEpisodes.items())
        '''map the text : link pairs into the seasonEpisodes dict'''
        episodesBySeason[k] = seasonEpisodes
    return episodesBySeason
    driver.close()

#seasons = getPlaylistUrls(playlistDir)
seasons = {'The Joy of Painting - Season 1': "https://www.youtube.com/playlist?list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu"}
masterEpisodes = getEpisodeUrls(seasons)
for k, v in masterEpisodes.items():
    print(k + '---------')
    for k2, v2 in v.items():
        print(k2 + ': ' + v2)
    print('\n\n')

print(masterEpisodes)
