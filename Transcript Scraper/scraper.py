import time
from bs4 import BeautifulSoup
import itertools
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

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
    driver.close()
    return episodesBySeason


def scrape(video_dict):
    print(video_dict)
    if not os.path.exists('Transcripts'):
        os.makedirs('Transcripts')
    os.chdir('Transcripts')
    driver = webdriver.Chrome()
    for season, season_dict in video_dict.items():
        if not os.path.exists(season):
            os.makedirs(season)
        os.chdir(season)
        cwd = os.getcwd()
        for episode_title, link in season_dict.items():
            if not os.path.exists(episode_title + '/' + episode_title + '.txt'):
                write_transcript(link, episode_title+'.txt', driver)
        os.chdir('..')


def write_transcript(link, outfile, driver):
    print(link + "hi")
    #driver.get("https://www.youtube.com/watch?v=wdr4t7cQW2U")
    driver.get(link)
    try:
        time.sleep(2)
        driver.find_element_by_xpath('//button[@aria-label="More actions"]').click()
        #elem = WebDriverWait(driver, 5).until(
         #   EC.visibility_of_element_located((By.XPATH, "//[@aria-label='More actions')]")))
        #elem.click()
        print('More Clicked')
        button = driver.find_element_by_xpath('//yt-formatted-string[contains(text(),"Open transcript")]')
        button.click()
        print("trans clicked")
        # open the Transcript so it gets sent to the DOM
        try:
            time.sleep(2)
            transcript = driver.find_element_by_xpath('//ytd-transcript-body-renderer')
            print(transcript)
            # Scrape the transcript from the DOM
        except TimeoutException:
            print("Timeout triggered, retrying...")
            autoCapMenu = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, './/span[text()="English (Automatic Captions)"]')))
            autoCapMenu.click()
            english = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH,
                                                  './/button[@value="en: English (Automatic Captions) - a.en"]')))
            english.click()
            """elem.click()
            time.sleep(1)
            button.click()
            time.sleep(1)"""
            transcript = WebDriverWait(driver, 4).until(
                EC.visibility_of_element_located((By.ID, 'transcript-scrollbox')))
        html = transcript.get_attribute('innerHTML')
        print(html)
        soup = BeautifulSoup(html, "html.parser")
        soup = soup.find_all("div", class_='cue style-scope ytd-transcript-body-renderer')
        vid_text = []
        count = 0
        try:
            for line in soup:
                temp = line.get_text().split()  # write each line to a list split by whitespace
                count += len(temp)
                vid_text = list(itertools.chain(vid_text, temp))  # chain the temp list of words into str
            print(vid_text)
            with open(outfile, "wb") as file:
                for word in vid_text:
                    word = word + '\n'
                    file.write(word.encode('utf8', 'ignore'))
                file.close()
        except IOError:
            print('error writing the file')
        print(str(len(vid_text)), " =?=  " + str(count))
        time.sleep(.1)
    except TimeoutException:
        print("woooops, top block timed out")

#seasons = getPlaylistUrls(playlistDir)
#masterEpisodes = getEpisodeUrls(seasons)
#print(masterEpisodes)
#time.sleep(5)
dutch = {'The Joy of Painting - Season 25': {'Bob Ross - Not Quite Spring (Season 25 Episode 3)': 'https://www.youtube.com/watch?v=N_u6x7LeyTM&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=3'},
         'The Joy of Painting - Season 2': {'Bob Ross - Reflections (Season 2 Episode 8)': 'https://www.youtube.com/watch?v=0FYfo94qefg&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=8'}}
masterEpisodes = {'The Joy of Painting - Season 31': {
    'Bob Ross - Reflections of Calm (Season 31 Episode 1)': 'https://www.youtube.com/watch?v=kJFB6rH3z2A&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=1',
    'Bob Ross - Before the Snowfall (Season 31 Episode 2)': 'https://www.youtube.com/watch?v=_MdMhQIOL1Y&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=2',
    'Bob Ross - Winding Stream (Season 31 Episode 3)': 'https://www.youtube.com/watch?v=QDwd4pMYyuo&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=3',
    'Bob Ross - Tranquility Cove (Season 31 Episode 4)': 'https://www.youtube.com/watch?v=7t6ue0pEcNE&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=4',
    'Bob Ross - Cabin in the Hollow (Season 31 Episode 5)': 'https://www.youtube.com/watch?v=KYlM2zJnNWY&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=5',
    'Bob Ross - View from Clear Creek (Season 31 Episode 6)': 'https://www.youtube.com/watch?v=TLX1bmS8wBE&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=6',
    'Bob Ross - Bridge to Autumn (Season 31 Episode 7)': 'https://www.youtube.com/watch?v=ReENCTH7MYI&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=7',
    "Bob Ross - Trail's End (Season 31 Episode 8)": 'https://www.youtube.com/watch?v=XWQrP-WiLgc&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=8',
    'Bob Ross - Evergreen Valley (Season 31 Episode 9)': 'https://www.youtube.com/watch?v=mEU0stNfkxI&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=9',
    'Bob Ross - Balmy Beach (Season 31 Episode 10)': 'https://www.youtube.com/watch?v=kMgd6r6c4vE&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=10',
    'Bob Ross - Lake at the Ridge (Season 31 Episode 11)': 'https://www.youtube.com/watch?v=8QWvzEQ69Kw&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=11',
    'Bob Ross - In the Midst of Winter (Season 31 Episode 12)': 'https://www.youtube.com/watch?v=qx2IsmrCs3c&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=12',
    'Bob Ross - Wilderness Day (Season 31 Episode 13)': 'https://www.youtube.com/watch?v=nJGCVFn57U8&list=PLAEQD0ULngi5PAjhOL-GfvbcQDn2Hujoj&index=13'},
                  'The Joy of Painting - Season 30': {
                      'Bob Ross - Babbling Brook (Season 30 Episode 1)': 'https://www.youtube.com/watch?v=ZHUdS0wEaKk&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=1',
                      'Bob Ross - Woodgrain View (Season 30 Episode 2)': 'https://www.youtube.com/watch?v=fcx1yUuSf3o&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=2',
                      "Bob Ross - Winter's Peace (Season 30 Episode 3)": 'https://www.youtube.com/watch?v=Xzv3iiWi1Wo&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=3',
                      'Bob Ross - Wilderness Trail (Season 30 Episode 4)': 'https://www.youtube.com/watch?v=vGsW_6BCukU&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=4',
                      'Bob Ross - A Copper Winter (Season 30 Episode 5)': 'https://www.youtube.com/watch?v=BSjee-ond7w&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=5',
                      'Bob Ross - Misty Foothills (Season 30 Episode 6)': 'https://www.youtube.com/watch?v=LEz4UVL7POE&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=6',
                      'Bob Ross - Through the Window (Season 30 Episode 7)': 'https://www.youtube.com/watch?v=SrN4A9rVXj0&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=7',
                      'Bob Ross - Home in the Valley (Season 30 Episode 8)': 'https://www.youtube.com/watch?v=enutOy-nsZk&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=8',
                      'Bob Ross - Mountains of Grace (Season 30 Episode 9)': 'https://www.youtube.com/watch?v=nXlu_Q0sR7c&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=9',
                      'Bob Ross - Seaside Harmony (Season 30 Episode 10)': 'https://www.youtube.com/watch?v=CY6sGFs209E&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=10',
                      'Bob Ross - A Cold Spring Day (Season 30 Episode 11)': 'https://www.youtube.com/watch?v=jq8bIbpW7DQ&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=11',
                      "Bob Ross - Evening's Glow (Season 30 Episode 12)": 'https://www.youtube.com/watch?v=eTEKGOi6SVg&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=12',
                      'Bob Ross - Blue Ridge Falls (Season 30 Episode 13)': 'https://www.youtube.com/watch?v=fz0YjqtHW84&list=PLAEQD0ULngi7EkzzzLDl33ibKHMDdUFc0&index=13'},
                  'The Joy of Painting - Season 29': {
                      'Bob Ross - Island in the Wilderness (Season 29 Episode 1)': 'https://www.youtube.com/watch?v=lLWEXRAnQd0&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=1',
                      'Bob Ross - Autumn Oval (Season 29 Episode 2)': 'https://www.youtube.com/watch?v=2XnIdinwot0&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=2',
                      'Bob Ross - Seasonal Progression (Season 29 Episode 3)': 'https://www.youtube.com/watch?v=T2G5waMfQ-g&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=3',
                      'Bob Ross - Light at the Summit (Season 29 Episode 4)': 'https://www.youtube.com/watch?v=HOdS-G8p1KE&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=4',
                      'Bob Ross - Countryside Barn (Season 29 Episode 5)': 'https://www.youtube.com/watch?v=G7Etn7QMeO4&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=5',
                      'Bob Ross - Mountain Lake Falls (Season 29 Episode 6)': 'https://www.youtube.com/watch?v=dNEp3hoHSDI&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=6',
                      'Bob Ross - Cypress Creek (Season 29 Episode 7)': 'https://www.youtube.com/watch?v=Tnb2cXKKuWM&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=7',
                      "Bob Ross - Trapper's Cabin (Season 29 Episode 8)": 'https://www.youtube.com/watch?v=chhCkmp0RG8&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=8',
                      'Bob Ross - Storm on the Horizon (Season 29 Episode 9)': 'https://www.youtube.com/watch?v=pA_2paUhBAQ&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=9',
                      "Bob Ross - Pot O' Posies (Season 29 Episode 10)": 'https://www.youtube.com/watch?v=2zv_S_uVoVQ&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=10',
                      'Bob Ross - A Perfect Winter Day (Season 29 Episode 11)': 'https://www.youtube.com/watch?v=Io4fwhacpEs&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=11',
                      "Bob Ross - Aurora's Dance (Season 29 Episode 12)": 'https://www.youtube.com/watch?v=iRMsb9Vf7GM&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=12',
                      "Bob Ross - Woodman's Retreat (Season 29 Episode 13)": 'https://www.youtube.com/watch?v=ODrV0dfQcNs&list=PLAEQD0ULngi6c0D5_ELtW5p_NLShDktAN&index=13'},
                  'The Joy of Painting - Season 28': {
                      "Bob Ross - Fisherman's Trail (Season 28 Episode 1)": 'https://www.youtube.com/watch?v=VnZEpic2UzU&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=1',
                      'Bob Ross - A Warm Winter (Season 28 Episode 2)': 'https://www.youtube.com/watch?v=_TTdw3YnXuo&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=2',
                      'Bob Ross - Under Pastel Skies (Season 28 Episode 3)': 'https://www.youtube.com/watch?v=lzODyJS2ZIg&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=3',
                      'Bob Ross - Golden Rays of Sunshine (Season 28 Episode 4)': 'https://www.youtube.com/watch?v=zxj3xLDNxo0&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=4',
                      'Bob Ross - The Magic of Fall (Season 28 Episode 5)': 'https://www.youtube.com/watch?v=bSm3fmEyJ20&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=5',
                      'Bob Ross - Glacier Lake (Season 28 Episode 6)': 'https://www.youtube.com/watch?v=TohG7F8M3Ls&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=6',
                      'Bob Ross - The Old Weathered Barn (Season 28 Episode 7)': 'https://www.youtube.com/watch?v=NYUIIBFj0iQ&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=7',
                      'Bob Ross - Deep Forest Falls (Season 28 Episode 8)': 'https://www.youtube.com/watch?v=urHQRbRNuYI&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=8',
                      "Bob Ross - Winter's Grace (Season 28 Episode 9)": 'https://www.youtube.com/watch?v=mxJ2On9wyvY&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=9',
                      'Bob Ross - Splendor of Autumn (Season 28 Episode 10)': 'https://www.youtube.com/watch?v=hEyR2FDp-00&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=10',
                      'Bob Ross - Tranquil Seas (Season 28 Episode 11)': 'https://www.youtube.com/watch?v=kN1DP_yqs-A&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=11',
                      'Bob Ross - Mountain Serenity (Season 28 Episode 12)': 'https://www.youtube.com/watch?v=wc_YVijYjT4&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=12',
                      'Bob Ross - Home Before Nightfall (Season 28 Episode 13)': 'https://www.youtube.com/watch?v=22SiIDvyJeM&list=PLAEQD0ULngi6tej39ptiDqix2wd-W6glj&index=13'},
                  'The Joy of Painting - Season 27': {
                      'Bob Ross - Twilight Beauty (Season 27 Episode 1)': 'https://www.youtube.com/watch?v=0mJqzzeWyXs&index=1&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      "Bob Ross - Angler's Haven (Season 27 Episode 2)": 'https://www.youtube.com/watch?v=XlwfcXZ0AIU&index=2&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Rustic Winter Woods (Season 27 Episode 3)': 'https://www.youtube.com/watch?v=3q8Zi9480lw&index=3&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Wilderness Falls (Season 27 Episode 4)': 'https://www.youtube.com/watch?v=gxd0MPX8c6I&index=4&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Winter at the Farm (Season 27 Episode 5)': 'https://www.youtube.com/watch?v=LeIVNKnWz7o&index=5&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Daisies at Dawn (Season 27 Episode 6)': 'https://www.youtube.com/watch?v=_kkZcIgocBM&index=6&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - A Spectacular View (Season 27 Episode 7)': 'https://www.youtube.com/watch?v=7R9HcaDT9P4&index=7&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Daybreak (Season 27 Episode 8)': 'https://www.youtube.com/watch?v=crWDcTvDmec&index=8&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Island Paradise (Season 27 Episode 9)': 'https://www.youtube.com/watch?v=Cg3XAVhAas0&index=9&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Sunlight in the Shadows (Season 27 Episode 10)': 'https://www.youtube.com/watch?v=xgjQ0v2d9mE&index=10&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Splendor of a Snowy Winter (Season 27 Episode 11)': 'https://www.youtube.com/watch?v=JdXCoxkOdwQ&index=11&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Forest River (Season 27 Episode 12)': 'https://www.youtube.com/watch?v=wrbGlR22K0Q&index=12&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG',
                      'Bob Ross - Golden Glow of Morning (Season 27 Episode 13)': 'https://www.youtube.com/watch?v=qXElmiqzcI0&index=13&list=PLAEQD0ULngi6J8P64GAMRZSzucIru0rMG'},
                  'The Joy of Painting - Season 26': {
                      'Bob Ross - In the Stillness of Morning (Season 26 Episode 1)': 'https://www.youtube.com/watch?v=5rfGa1_iJpw&index=1&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - Delightful Meadow Home (Season 26 Episode 2)': 'https://www.youtube.com/watch?v=tWoInh2USOs&index=2&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - First Snow (Season 26 Episode 3)': 'https://www.youtube.com/watch?v=raAkJKeo0Sk&index=3&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - Lake in the Valley (Season 26 Episode 4)': 'https://www.youtube.com/watch?v=KvJmSrErm20&index=4&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - A Trace of Spring (Season 26 Episode 5)': 'https://www.youtube.com/watch?v=JMPwj3u4ZTA&index=5&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - An Arctic Winter Day (Season 26 Episode 6)': 'https://www.youtube.com/watch?v=9BHWlbjd95c&index=6&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - Snow Birch (Season 26 Episode 7)': 'https://www.youtube.com/watch?v=wKeemvioVrM&index=7&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - Early Autumn (Season 26 Episode 8)': 'https://www.youtube.com/watch?v=SLQXlFLoqQc&index=8&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - Tranquil Wooded Stream (Season 26 Episode 9)': 'https://www.youtube.com/watch?v=lSeRrm5ZK9c&index=9&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - Purple Mountain Range (Season 26 Episode 10)': 'https://www.youtube.com/watch?v=nkDA_R-XmqA&index=10&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      "Bob Ross - Storm's A Comin (Season 26 Episode 11)": 'https://www.youtube.com/watch?v=EHD9u-lo2wc&index=11&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - Sunset Aglow (Season 26 Episode 12)': 'https://www.youtube.com/watch?v=gMEZp47VKC0&index=12&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39',
                      'Bob Ross - Evening at the Falls (Season 26 Episode 13)': 'https://www.youtube.com/watch?v=RulXVcpgpqw&index=13&list=PLAEQD0ULngi5c9XxQCtE8zGh157RJWH39'},
                  'The Joy of Painting - Season 25': {
                      'Bob Ross - Hide A Way Cove (Season 25 Episode 1)': 'https://www.youtube.com/watch?v=l_HqMYquc08&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=1',
                      'Bob Ross - Enchanted Falls Oval (Season 25 Episode 2)': 'https://www.youtube.com/watch?v=HklPkQ0lSKA&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=2',
                      'Bob Ross - Not Quite Spring (Season 25 Episode 3)': 'https://www.youtube.com/watch?v=N_u6x7LeyTM&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=3',
                      'Bob Ross - Splashes of Autumn (Season 25 Episode 4)': 'https://www.youtube.com/watch?v=YcbaMqq_X8s&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=4',
                      'Bob Ross - Summer in the Mountain (Season 25 Episode 5)': 'https://www.youtube.com/watch?v=gmCXgS38NDc&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=5',
                      'Bob Ross - Oriental Falls (Season 25 Episode 6)': 'https://www.youtube.com/watch?v=v8Znj8bbmCQ&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=6',
                      'Bob Ross - Autumn Palette (Season 25 Episode 7)': 'https://www.youtube.com/watch?v=HWrvW-NgaOY&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=7',
                      'Bob Ross - Cypress Swamp (Season 25 Episode 8)': 'https://www.youtube.com/watch?v=FdIUHudQABI&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=8',
                      'Bob Ross - Downstream View (Season 25 Episode 9)': 'https://www.youtube.com/watch?v=KsDPg5HZYNw&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=9',
                      'Bob Ross - Just Before the Storm (Season 25 Episode 10)': 'https://www.youtube.com/watch?v=Rh-jKrMrmOA&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=10',
                      "Bob Ross - Fisherman's Paradise (Season 25 Episode 11)": 'https://www.youtube.com/watch?v=uJLK85uU5mA&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=11',
                      'Bob Ross - Desert Hues (Season 25 Episode 12)': 'https://www.youtube.com/watch?v=UUNNXGVNTuI&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=12',
                      'Bob Ross - The Property Line (Season 25 Episode 13)': 'https://www.youtube.com/watch?v=ivesI3rU7dU&list=PLAEQD0ULngi6XUucZGmcQeVRGHNg2WVsB&index=13'},
                  'The Joy of Painting - Season 24': {
                      'Bob Ross - Gray Mountain (Season 24 Episode 1)': 'https://www.youtube.com/watch?v=4XxClvPZ1RE&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=1',
                      'Bob Ross - Wayside Pond (Season 24 Episode 2)': 'https://www.youtube.com/watch?v=FPW2FwK4IOo&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=2',
                      'Bob Ross - Teton Winter (Season 24 Episode 3)': 'https://www.youtube.com/watch?v=I4h6TC4CPJY&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=3',
                      'Bob Ross - Little Home in the Meadow (Season 24 Episode 4)': 'https://www.youtube.com/watch?v=nU1zV93N-kI&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=4',
                      'Bob Ross - A Pretty Autumn Day (Season 24 Episode 5)': 'https://www.youtube.com/watch?v=HWedDS3p7XI&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=5',
                      'Bob Ross - Mirrored Images (Season 24 Episode 6)': 'https://www.youtube.com/watch?v=i29frkR1T98&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=6',
                      'Bob Ross - Back-Country Path (Season 24 Episode 7)': 'https://www.youtube.com/watch?v=2iNMoQB1Pe8&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=7',
                      'Bob Ross - Graceful Waterfall (Season 24 Episode 8)': 'https://www.youtube.com/watch?v=fBh1nA4pMDY&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=8',
                      'Bob Ross - Icy Lake (Season 24 Episode 9)': 'https://www.youtube.com/watch?v=AmBDmgta3l4&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=9',
                      'Bob Ross - Rowboat on the Beach (Season 24 Episode 10)': 'https://www.youtube.com/watch?v=hfvhXOvg43w&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=10',
                      'Bob Ross - Portrait of Winter (Season 24 Episode 11)': 'https://www.youtube.com/watch?v=JLnIUGOupOA&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=11',
                      'Bob Ross - The Footbridge (Season 24 Episode 12)': 'https://www.youtube.com/watch?v=RqtDliGeyTg&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=12',
                      'Bob Ross - Snowbound Cabin (Season 24 Episode 13)': 'https://www.youtube.com/watch?v=obSLZWXmDak&list=PLAEQD0ULngi5ot5FztonBZegKLnsa1gXC&index=13'},
                  'The Joy of Painting - Season 23': {
                      'Bob Ross - Frosty Winter Morn (Season 23 Episode 1)': 'https://www.youtube.com/watch?v=1-9_enMBquw&index=1&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Forest Edge (Season 23 Episode 2)': 'https://www.youtube.com/watch?v=puGk2iFvvp0&index=2&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Mountain Ridge Lake (Season 23 Episode 3)': 'https://www.youtube.com/watch?v=Hq-z06i6HCs&index=3&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Reflections of Gold (Season 23 Episode 4)': 'https://www.youtube.com/watch?v=8f9CCnqJ_1Y&index=4&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Quiet Cove (Season 23 Episode 5)': 'https://www.youtube.com/watch?v=cR9hTbSomx4&index=5&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Rivers Peace (Season 23 Episode 6)': 'https://www.youtube.com/watch?v=flCWS9LB4Ks&index=6&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      "Bob Ross - At Dawn's Light (Season 23 Episode 7)": 'https://www.youtube.com/watch?v=HFdTxqEznIk&index=7&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Valley Waterfall (Season 23 Episode 8)': 'https://www.youtube.com/watch?v=VYcsYzzRae4&index=8&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Toward Days End (Season 23 Episode 9)': 'https://www.youtube.com/watch?v=cFi_fJl40BA&index=9&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Falls in the Glen (Season 23 Episode 10)': 'https://www.youtube.com/watch?v=txAtX-VyVNc&index=10&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Frozen Beauty in Vignette (Season 23 Episode 11)': 'https://www.youtube.com/watch?v=H15kV1wbDG4&index=11&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Crimson Tide (Season 23 Episode 12)': 'https://www.youtube.com/watch?v=Y7SDU4i6Fco&index=12&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a',
                      'Bob Ross - Winter Bliss (Season 23 Episode 13)': 'https://www.youtube.com/watch?v=yInYwy6AsDQ&index=13&list=PLAEQD0ULngi6dGd30_mzWENbNpT1k844a'},
                  'The Joy of Painting - Season 22': {
                      'Bob Ross - Autumn Images (Season 22 Episode 1)': 'https://www.youtube.com/watch?v=HMx34Am6RFg&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=1',
                      'Bob Ross - Hint of Springtime (Season 22 Episode 2)': 'https://www.youtube.com/watch?v=C-OSaHvt8ms&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=2',
                      'Bob Ross - Around the Bend (Season 22 Episode 3)': 'https://www.youtube.com/watch?v=Kl5X3icOVvw&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=3',
                      'Bob Ross - Countryside Oval (Season 22 Episode 4)': 'https://www.youtube.com/watch?v=hdNH5axK4u0&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=4',
                      'Bob Ross - Russet Winter (Season 22 Episode 5)': 'https://www.youtube.com/watch?v=aE4nID1p-t0&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=5',
                      'Bob Ross - Purple Haze (Season 22 Episode 6)': 'https://www.youtube.com/watch?v=ZoJ2tcXWb7g&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=6',
                      'Bob Ross - Dimensions (Season 22 Episode 7)': 'https://www.youtube.com/watch?v=JUuP75RVZDI&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=7',
                      'Bob Ross - Deep Wilderness Home (Season 22 Episode 8)': 'https://www.youtube.com/watch?v=uZWNvDFfbUk&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=8',
                      'Bob Ross - Haven in the Valley (Season 22 Episode 9)': 'https://www.youtube.com/watch?v=Qccgam514ds&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=9',
                      'Bob Ross - Wintertime Blues (Season 22 Episode 10)': 'https://www.youtube.com/watch?v=dbMJVM4iL2Q&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=10',
                      'Bob Ross - Pastel Seascape (Season 22 Episode 11)': 'https://www.youtube.com/watch?v=K4aud_SpFDQ&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=11',
                      'Bob Ross - Country Creek (Season 22 Episode 12)': 'https://www.youtube.com/watch?v=JDa6JPcqy88&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=12',
                      'Bob Ross - Silent Forest (Season 22 Episode 13)': 'https://www.youtube.com/watch?v=AE1GKcL3NuI&list=PLAEQD0ULngi5b8jcMLQ003OV5C2qUNeFE&index=13'},
                  'The Joy of Painting - Season 21': {
                      'Bob Ross - Valley View (Season 21 Episode 1)': 'https://www.youtube.com/watch?v=pw5ETGiiBRg&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=1',
                      'Bob Ross - Tranquil Dawn (Season 21 Episode 2)': 'https://www.youtube.com/watch?v=4abDq6Q-mlM&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=2',
                      'Bob Ross - Royal Majesty (Season 21 Episode 3)': 'https://www.youtube.com/watch?v=ubUXBqE6t0U&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=3',
                      'Bob Ross - Serenity (Season 21 Episode 4)': 'https://www.youtube.com/watch?v=crqmO3qDdco&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=4',
                      'Bob Ross - Cabin at Trails End (Season 21 Episode 5)': 'https://www.youtube.com/watch?v=GLkLO4KqTRs&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=5',
                      'Bob Ross - Mountain Rhapsody (Season 21 Episode 6)': 'https://www.youtube.com/watch?v=H4VsmKU5T7g&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=6',
                      'Bob Ross - Wilderness Cabin (Season 21 Episode 7)': 'https://www.youtube.com/watch?v=GWehiacnd1E&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=7',
                      'Bob Ross - By the Sea (Season 21 Episode 8)': 'https://www.youtube.com/watch?v=8tHHBTK6wwc&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=8',
                      'Bob Ross - Indian Summer (Season 21 Episode 9)': 'https://www.youtube.com/watch?v=pfWV8NkotvU&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=9',
                      'Bob Ross - Blue Winter (Season 21 Episode 10)': 'https://www.youtube.com/watch?v=liR0gS0sZY0&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=10',
                      'Bob Ross - Desert Glow (Season 21 Episode 11)': 'https://www.youtube.com/watch?v=QyncJfL_HmU&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=11',
                      'Bob Ross - Lone Mountain (Season 21 Episode 12)': 'https://www.youtube.com/watch?v=NJbzIftLLmU&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=12',
                      "Bob Ross - Florida's Glory (Season 21 Episode 13)": 'https://www.youtube.com/watch?v=HQC5sPN9Xhc&list=PLAEQD0ULngi5_UcEWkQZu23WzQP1Tkxq3&index=13'},
                  'The Joy of Painting - Season 20': {
                      'Bob Ross - Mystic Mountain (Season 20 Episode 1)': 'https://www.youtube.com/watch?v=VlucWfTUo1A&index=1&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      "Bob Ross - New Day's Dawn (Season 20 Episode 2)": 'https://www.youtube.com/watch?v=vbPdQ0w8ylg&index=2&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Winter in Pastel (Season 20 Episode 3)': 'https://www.youtube.com/watch?v=kbnXZRNMouM&index=3&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Hazy Day (Season 20 Episode 4)': 'https://www.youtube.com/watch?v=5U3G61r35Mc&index=4&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Divine Elegance (Season 20 Episode 5)': 'https://www.youtube.com/watch?v=mb-Gwx1S5Gs&index=5&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Cliffside (Season 20 Episode 6)': 'https://www.youtube.com/watch?v=p6Uy2qOLvGk&index=6&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Autumn Fantasy (Season 20 Episode 7)': 'https://www.youtube.com/watch?v=FozIp7Va7dY&index=7&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - The Old Oak Tree (Season 20 Episode 8)': 'https://www.youtube.com/watch?v=dN4HjAn8p5U&index=8&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Winter Paradise (Season 20 Episode 9)': 'https://www.youtube.com/watch?v=DY1aBv8Z1SQ&index=9&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Days Gone By (Season 20 Episode 10)': 'https://www.youtube.com/watch?v=DmYhNHVIdMI&index=10&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Change of Seasons (Season 20 Episode 11)': 'https://www.youtube.com/watch?v=QbgPu5f2Vf8&index=11&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Hidden Delight (Season 20 Episode 12)': 'https://www.youtube.com/watch?v=ZyPNzDaaDt8&index=12&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Double Take (Season 20 Episode 13)': 'https://www.youtube.com/watch?v=ppzFgG2K2k4&index=13&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM',
                      'Bob Ross - Mystic Mountain (High Quality) - Season 20 Episode 1': 'https://www.youtube.com/watch?v=3AHdKAu055M&index=14&list=PLAEQD0ULngi7-jK4pdhsSiu5CC0ojRqmM'},
                  'The Joy of Painting - Season 19': {
                      'Bob Ross - Snowfall Magic (Season 19 Episode 1)': 'https://www.youtube.com/watch?v=1enWTsRi16o&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=1',
                      'Bob Ross - Quiet Mountain Lake (Season 19 Episode 2)': 'https://www.youtube.com/watch?v=2gq2V6dCt2I&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=2',
                      'Bob Ross - Final Embers of Sunlight (Season 19 Episode 3)': 'https://www.youtube.com/watch?v=IeFbdk36MUU&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=3',
                      'Bob Ross - Snowy Morn (Season 19 Episode 4)': 'https://www.youtube.com/watch?v=iB1TDWlo0kk&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=4',
                      "Bob Ross - Camper's Haven (Season 19 Episode 5)": 'https://www.youtube.com/watch?v=C34WAUgkAT0&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=5',
                      'Bob Ross - Waterfall in the Woods (Season 19 Episode 6)': 'https://www.youtube.com/watch?v=uBRKVa7sy1Q&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=6',
                      'Bob Ross - Covered Bridge Oval (Season 19 Episode 7)': 'https://www.youtube.com/watch?v=F4iPbH1OHsQ&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=7',
                      'Bob Ross - Scenic Seclusion (Season 19 Episode 8)': 'https://www.youtube.com/watch?v=d50HkqB9JEM&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=8',
                      'Bob Ross - Ebb Tide (Season 19 Episode 9)': 'https://www.youtube.com/watch?v=mFOna_LN7Ys&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=9',
                      'Bob Ross - After the Rain (Season 19 Episode 10)': 'https://www.youtube.com/watch?v=Wj-3ct7RvAI&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=10',
                      'Bob Ross - Winter Elegance (Season 19 Episode 11)': 'https://www.youtube.com/watch?v=JjBZzKp_u5E&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=11',
                      "Bob Ross - Evening's Peace (Season 19 Episode 12)": 'https://www.youtube.com/watch?v=uEUMVwc4o5U&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=12',
                      'Bob Ross - Valley of Tranquility (Season 19 Episode 13)': 'https://www.youtube.com/watch?v=FnY7jDY5PsE&list=PLAEQD0ULngi56cKK-XkgZPwVLZ0lI15Mn&index=13'},
                  'The Joy of Painting - Season 18': {
                      'Bob Ross - Half-Oval Vignette (Season 18 Episode 1)': 'https://www.youtube.com/watch?v=uY3fIry2tOE&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=1',
                      'Bob Ross - Absolutely Autumn (Season 18 Episode 2)': 'https://www.youtube.com/watch?v=PGPVpil2UmE&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=2',
                      'Bob Ross - Mountain Seclusion (Season 18 Episode 3)': 'https://www.youtube.com/watch?v=EBZKuVbRY54&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=3',
                      'Bob Ross - Crimson Oval (Season 18 Episode 4)': 'https://www.youtube.com/watch?v=R7Y3izMFPbM&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=4',
                      'Bob Ross - Autumn Exhibition (Season 18 Episode 5)': 'https://www.youtube.com/watch?v=6afHY2d9Lv8&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=5',
                      'Bob Ross - Majestic Peaks (Season 18 Episode 6)': 'https://www.youtube.com/watch?v=lilbzLCNnDo&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=6',
                      'Bob Ross - Golden Morning Mist (Season 18 Episode 7)': 'https://www.youtube.com/watch?v=rCHXqj4DHlM&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=7',
                      'Bob Ross - Winter Lace (Season 18 Episode 8)': 'https://www.youtube.com/watch?v=WJF_qoQRPck&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=8',
                      'Bob Ross - Seascape Fantasy (Season 18 Episode 9)': 'https://www.youtube.com/watch?v=sBBBilrDuSw&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=9',
                      'Bob Ross - Double Oval Stream (Season 18 Episode 10)': 'https://www.youtube.com/watch?v=rRjnHdr9DmU&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=10',
                      'Bob Ross - Enchanted Forest (Season 18 Episode 11)': 'https://www.youtube.com/watch?v=ikR7UT9mVBw&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=11',
                      'Bob Ross - Southwest Serenity (Season 18 Episode 12)': 'https://www.youtube.com/watch?v=EVfPPJ5FUmA&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=12',
                      'Bob Ross - Rippling Waters (Season 18 Episode 13)': 'https://www.youtube.com/watch?v=XvnJBynSiT0&list=PLAEQD0ULngi79FbgDR5HQURtzgXlRUfYa&index=13'},
                  'The Joy of Painting - Season 17': {
                      'Bob Ross - Golden Mist Oval (Season 17 Episode 1)': 'https://www.youtube.com/watch?v=lhpfaW0k6uM&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=1',
                      'Bob Ross - The Old Home Place (Season 17 Episode 2)': 'https://www.youtube.com/watch?v=EVQcDEiJh2o&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=2',
                      'Bob Ross - Soothing Vista (Season 17 Episode 3)': 'https://www.youtube.com/watch?v=NqfRLiv0SZ0&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=3',
                      'Bob Ross - Stormy Seas (Season 17 Episode 4)': 'https://www.youtube.com/watch?v=LE6agCR5iBw&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=4',
                      'Bob Ross - Country Time (Season 17 Episode 5)': 'https://www.youtube.com/watch?v=e_bt9rQoGN0&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=5',
                      "Bob Ross - A Mild Winter's Day (Season 17 Episode 6)": 'https://www.youtube.com/watch?v=BbYO579MmhA&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=6',
                      'Bob Ross - Spectacular Waterfall (Season 17 Episode 7)': 'https://www.youtube.com/watch?v=nK-HebXL2uw&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=7',
                      'Bob Ross - View from the Park (Season 17 Episode 8)': 'https://www.youtube.com/watch?v=Q4n90jsOUtY&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=8',
                      'Bob Ross - Lake View (Season 17 Episode 9)': 'https://www.youtube.com/watch?v=07acfzBaoa0&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=9',
                      'Bob Ross - Old Country Mill (Season 17 Episode 10)': 'https://www.youtube.com/watch?v=n8HlFCQACYA&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=10',
                      'Bob Ross - Morning Walk (Season 17 Episode 11)': 'https://www.youtube.com/watch?v=pSvgNkQdR2Y&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=11',
                      "Bob Ross - Nature's Splendor (Season 17 Episode 12)": 'https://www.youtube.com/watch?v=uCAtI2IwEwk&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=12',
                      'Bob Ross - Mountain Beauty (Season 17 Episode 13)': 'https://www.youtube.com/watch?v=8P-YeoTmVrw&list=PLAEQD0ULngi5jejZ_dD7KhhEoLbjmglar&index=13'},
                  'The Joy of Painting - Season 16': {
                      'Bob Ross - Two Seasons (Season 16 Episode 1)': 'https://www.youtube.com/watch?v=jwVz0uTLH1I&index=1&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Nestled Cabin (Season 16 Episode 2)': 'https://www.youtube.com/watch?v=l_jN9KN257M&index=2&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Wintertime Discovery (Season 16 Episode 3)': 'https://www.youtube.com/watch?v=uZyZW3tkCE0&index=3&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Mountain Mirage Wood Shape (Season 16 Episode 4)': 'https://www.youtube.com/watch?v=jfCsew_mz7A&index=4&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Double Oval Fantasy (Season 16 Episode 5)': 'https://www.youtube.com/watch?v=4jAsLpJzjHM&index=5&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Contemplative Lady (Season 16 Episode 6)': 'https://www.youtube.com/watch?v=gnp6WE7Ql-s&index=6&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Deep Woods (Season 16 Episode 7)': 'https://www.youtube.com/watch?v=rE5ZVs_YJfE&index=7&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - High Tide (Season 16 Episode 8)': 'https://www.youtube.com/watch?v=_IREQ4SIcX8&index=8&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Barn in Snow Oval (Season 16 Episode 9)': 'https://www.youtube.com/watch?v=wJmi7-G9r-w&index=9&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - That Time of Year (Season 16 Episode 10)': 'https://www.youtube.com/watch?v=q5moLoqOkP0&index=10&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Waterfall Wonder (Season 16 Episode 11)': 'https://www.youtube.com/watch?v=AGhXEPfp-W4&index=11&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Mighty Mountain Lake (Season 16 Episode 12)': 'https://www.youtube.com/watch?v=4vXB2R8ybDE&index=12&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo',
                      'Bob Ross - Wooded Stream Oval (Season 16 Episode 13)': 'https://www.youtube.com/watch?v=-XA2h17y3HU&index=13&list=PLAEQD0ULngi759CWjXUQM4IUE0fCn-REo'},
                  'The Joy of Painting - Season 15': {
                      'Bob Ross - Splendor of Winter (Season 15 Episode 1)': 'https://www.youtube.com/watch?v=oJvk7gPDHiE&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=1',
                      'Bob Ross - Colors of Nature (Season 15 Episode 2)': 'https://www.youtube.com/watch?v=Me9Ietooq4w&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=2',
                      "Bob Ross - Grandpa's Barn (Season 15 Episode 3)": 'https://www.youtube.com/watch?v=IPPU49PyfEA&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=3',
                      'Bob Ross - Peaceful Reflections (Season 15 Episode 4)': 'https://www.youtube.com/watch?v=gYuH4Ilqdhs&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=4',
                      'Bob Ross - Hidden Winter Moon Oval (Season 15 Episode 5)': 'https://www.youtube.com/watch?v=yxAMOdl6RJE&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=5',
                      'Bob Ross - Waves of Wonder (Season 15 Episode 6)': 'https://www.youtube.com/watch?v=tayQX_ng-Nc&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=6',
                      'Bob Ross - Cabin by the Pond (Season 15 Episode 7)': 'https://www.youtube.com/watch?v=TyOO6WeP2AY&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=7',
                      'Bob Ross - Fall Stream (Season 15 Episode 8)': 'https://www.youtube.com/watch?v=ZY0ofhdV_L0&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=8',
                      'Bob Ross - Christmas Eve Snow (Season 15 Episode 9)': 'https://www.youtube.com/watch?v=cVqFG2pxK2A&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=9',
                      'Bob Ross - Forest Down Oval (Season 15 Episode 10)': 'https://www.youtube.com/watch?v=COsJUfPN2dA&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=10',
                      'Bob Ross - Pathway to Autumn (Season 15 Episode 11)': 'https://www.youtube.com/watch?v=Hg5RKc6xiL4&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=11',
                      'Bob Ross - Deep Forest Lake (Season 15 Episode 12)': 'https://www.youtube.com/watch?v=2bjFmSQjQrw&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=12',
                      'Bob Ross - Peaks of Majesty (Season 15 Episode 13)': 'https://www.youtube.com/watch?v=lTb8DN6G6dE&list=PLAEQD0ULngi78t8tWZw6zPofUY5_Tz6AU&index=13'},
                  'The Joy of Painting - Season 14': {
                      'Bob Ross - Distant Mountains (Season 14 Episode 1)': 'https://www.youtube.com/watch?v=GpA9UM7QGag&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=1',
                      'Bob Ross - Meadow Brook Surprise (Season 14 Episode 2)': 'https://www.youtube.com/watch?v=Ov5oIHTAa10&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=2',
                      'Bob Ross - Mountain Moonlight Oval (Season 14 Episode 3)': 'https://www.youtube.com/watch?v=CigXQtT6BPM&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=3',
                      'Bob Ross - Snowy Solitude (Season 14 Episode 4)': 'https://www.youtube.com/watch?v=1ZriQGhSFTM&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=4',
                      'Bob Ross - Mountain River (Season 14 Episode 5)': 'https://www.youtube.com/watch?v=CnMLKAGi0yM&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=5',
                      'Bob Ross - Graceful Mountains (Season 14 Episode 6)': 'https://www.youtube.com/watch?v=0uVe8T-vVVg&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=6',
                      'Bob Ross - Windy Waves (Season 14 Episode 7)': 'https://www.youtube.com/watch?v=y6GVVjG4HMg&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=7',
                      'Bob Ross - On a Clear Day (Season 14 Episode 8)': 'https://www.youtube.com/watch?v=e63Cgln6Yag&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=8',
                      'Bob Ross - Riverside Escape Oval (Season 14 Episode 9)': 'https://www.youtube.com/watch?v=d83REwSGfGo&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=9',
                      'Bob Ross - Surprising Falls (Season 14 Episode 10)': 'https://www.youtube.com/watch?v=QbclL1ca7_s&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=10',
                      'Bob Ross - Shadow Pond (Season 14 Episode 11)': 'https://www.youtube.com/watch?v=BQWJ3kqonpA&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=11',
                      'Bob Ross - Misty Forest Oval (Season 14 Episode 12)': 'https://www.youtube.com/watch?v=ddU9vQvSpw8&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=12',
                      'Bob Ross - Natural Wonder (Season 14 Episode 13)': 'https://www.youtube.com/watch?v=knOutsaiKfU&list=PLAEQD0ULngi4tDLpPnT7XV0hzcIKMZLlP&index=13'},
                  'The Joy of Painting - Season 13': {
                      'Bob Ross - Rolling Hills (Season 13 Episode 1)': 'https://www.youtube.com/watch?v=H4GyGrT7lEQ&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=1',
                      'Bob Ross - Frozen Solitude (Season 13 Episode 2)': 'https://www.youtube.com/watch?v=kNZssD9zWlw&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=2',
                      'Bob Ross - Meadow Brook (Season 13 Episode 3)': 'https://www.youtube.com/watch?v=06W8GsWj2Yg&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=3',
                      'Bob Ross - Evening at Sunset (Season 13 Episode 4)': 'https://www.youtube.com/watch?v=7ZUQTXuDPaI&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=4',
                      'Bob Ross - Mountain View (Season 13 Episode 5)': 'https://www.youtube.com/watch?v=dJfnAyDLwPY&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=5',
                      'Bob Ross - Hidden Creek (Season 13 Episode 6)': 'https://www.youtube.com/watch?v=KmoRz01bm0Y&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=6',
                      'Bob Ross - Peaceful Haven (Season 13 Episode 7)': 'https://www.youtube.com/watch?v=j20pZ96E_CE&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=7',
                      'Bob Ross - Mountain Exhibition (Season 13 Episode 8)': 'https://www.youtube.com/watch?v=bgI3_1quJ18&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=8',
                      'Bob Ross - Emerald Waters (Season 13 Episode 9)': 'https://www.youtube.com/watch?v=lLunPQBzW6g&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=9',
                      'Bob Ross - Mountain Summit (Season 13 Episode 10)': 'https://www.youtube.com/watch?v=kasGRkfkiPM&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=10',
                      'Bob Ross - Cabin Hideaway (Season 13 Episode 11)': 'https://www.youtube.com/watch?v=NjTlW2NL1Lo&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=11',
                      'Bob Ross - Oval Essence (Season 13 Episode 12)': 'https://www.youtube.com/watch?v=q7WXF_BSEXw&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=12',
                      'Bob Ross - Lost Lake (Season 13 Episode 13)': 'https://www.youtube.com/watch?v=9-ATP8xyDM0&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=13'},
                  'The Joy of Painting - Season 12': {
                      'Bob Ross - Golden Knoll (Season 12 Episode 1)': 'https://www.youtube.com/watch?v=-O0Bs65eN5w&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=1',
                      'Bob Ross - Mountain Reflections (Season 12 Episode 2)': 'https://www.youtube.com/watch?v=rzYpa4XGSnA&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=2',
                      'Bob Ross - Secluded Mountain (Season 12 Episode 3)': 'https://www.youtube.com/watch?v=3PZabdohLso&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=3',
                      'Bob Ross - Bright Autumn Trees (Season 12 Episode 4)': 'https://www.youtube.com/watch?v=aR-C3h5zURM&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=4',
                      'Bob Ross - Black Seascape (Season 12 Episode 5)': 'https://www.youtube.com/watch?v=P_aCan4cBwc&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=5',
                      'Bob Ross - Steep Mountains (Season 12 Episode 6)': 'https://www.youtube.com/watch?v=fRK8_ioYWw4&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=6',
                      'Bob Ross - Quiet Mountains River (Season 12 Episode 7)': 'https://www.youtube.com/watch?v=Leiw-FtADZc&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=7',
                      'Bob Ross - Evening Waterfall (Season 12 Episode 8)': 'https://www.youtube.com/watch?v=PutvF_P4588&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=8',
                      'Bob Ross - Tropical Seascape (Season 12 Episode 9)': 'https://www.youtube.com/watch?v=RrBsbqO9aqI&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=9',
                      'Bob Ross - Mountain at Sunset (Season 12 Episode 10)': 'https://www.youtube.com/watch?v=HCsCatvigtw&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=10',
                      'Bob Ross - Soft Mountain Glow (Season 12 Episode 11)': 'https://www.youtube.com/watch?v=gOGJYHWjXgE&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=11',
                      'Bob Ross - Mountain in an Oval (Season 12 Episode 12)': 'https://www.youtube.com/watch?v=1jRPshs27H8&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=12',
                      'Bob Ross - Winter Mountain (Season 12 Episode 13)': 'https://www.youtube.com/watch?v=46vI20697HI&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=13'},
                  'The Joy of Painting - Season 11': {
                      'Bob Ross - Mountain Stream (Season 11 Episode 1)': 'https://www.youtube.com/watch?v=xdFCj6BzQio&index=1&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Country Cabin (Season 11 Episode 2)': 'https://www.youtube.com/watch?v=Dkww2nHpuZw&index=2&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Daisy Delight (Season 11 Episode 3)': 'https://www.youtube.com/watch?v=HuHC1RqtvDA&index=3&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Hidden Stream (Season 11 Episode 4)': 'https://www.youtube.com/watch?v=JGzTg8fCj4w&index=4&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Towering Glacier (Season 11 Episode 5)': 'https://www.youtube.com/watch?v=67vdGbA3Xkg&index=5&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Oval Barn (Season 11 Episode 6)': 'https://www.youtube.com/watch?v=HqBhCibidNM&index=6&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Lakeside Path (Season 11 Episode 7)': 'https://www.youtube.com/watch?v=1yjGoJokbZg&index=7&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Sunset Oval (Season 11 Episode 8)': 'https://www.youtube.com/watch?v=9xG6IzcGotI&index=8&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Winter Barn (Season 11 Episode 9)': 'https://www.youtube.com/watch?v=_xkn0ceDreo&index=9&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Sunset over the Waves (Season 11 Episode 10)': 'https://www.youtube.com/watch?v=c4b_B2F1eZg&index=10&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Golden Glow (Season 11 Episode 11)': 'https://www.youtube.com/watch?v=aA8RhtaWACA&index=11&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Roadside Barn (Season 11 Episode 12)': 'https://www.youtube.com/watch?v=vJpKhiXvXdA&index=12&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M',
                      'Bob Ross - Happy Accident (Season 11 Episode 13)': 'https://www.youtube.com/watch?v=Fw6odlNp7_8&index=13&list=PLAEQD0ULngi7aIB4ifBbRHlAmsWpDko5M'},
                  'The Joy of Painting - Season 10': {
                      'Bob Ross - Towering Peaks (Season 10 Episode 1)': 'https://www.youtube.com/watch?v=1s58rW0_LN4&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=1',
                      'Bob Ross - Cabin at Sunset (Season 10 Episode 2)': 'https://www.youtube.com/watch?v=a6Wil3OXNuI&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=2',
                      'Bob Ross - Twin Falls (Season 10 Episode 3)': 'https://www.youtube.com/watch?v=cMwkY8ojRik&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=3',
                      'Bob Ross - Secluded Bridge (Season 10 Episode 4)': 'https://www.youtube.com/watch?v=vrAMRxBB5KI&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=4',
                      'Bob Ross - Ocean Breeze (Season 10 Episode 5)': 'https://www.youtube.com/watch?v=XZmdzfvXRuw&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=5',
                      'Bob Ross - Autumn Woods (Season 10 Episode 6)': 'https://www.youtube.com/watch?v=vKyMU5Z8cDI&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=6',
                      'Bob Ross - Winter Solitude (Season 10 Episode 7)': 'https://www.youtube.com/watch?v=ov4YaCQB9co&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=7',
                      'Bob Ross - Golden Sunset (Season 10 Episode 8)': 'https://www.youtube.com/watch?v=CiNDyckERXQ&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=8',
                      'Bob Ross - Mountain Oval (Season 10 Episode 9)': 'https://www.youtube.com/watch?v=Qj6lMtnCt8o&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=9',
                      'Bob Ross - Ocean Sunset (Season 10 Episode 10)': 'https://www.youtube.com/watch?v=OJ_xqtvZf3o&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=10',
                      'Bob Ross - Triple View (Season 10 Episode 11)': 'https://www.youtube.com/watch?v=zoTeyliLn5o&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=11',
                      'Bob Ross - Winter Frost (Season 10 Episode 12)': 'https://www.youtube.com/watch?v=8satX-hLkuI&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=12',
                      'Bob Ross - Lakeside Cabin (Season 10 Episode 13)': 'https://www.youtube.com/watch?v=1l_TsfCIb_I&list=PLAEQD0ULngi5nVGjPmjw-vCE5AuDTLkkQ&index=13'},
                  'The Joy of Painting - Season 9': {
                      'Bob Ross - Winter Evergreens (Season 9 Episode 1)': 'https://www.youtube.com/watch?v=O6L5YPt9CeU&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=1',
                      "Bob Ross - Surf's Up (Season 9 Episode 2)": 'https://www.youtube.com/watch?v=ZKxFvyyOBPQ&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=2',
                      'Bob Ross - Red Sunset (Season 9 Episode 3)': 'https://www.youtube.com/watch?v=e5JhYi_G-l0&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=3',
                      'Bob Ross - Meadow Road (Season 9 Episode 4)': 'https://www.youtube.com/watch?v=u5VT_WGM0kg&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=4',
                      'Bob Ross - Winter Oval (Season 9 Episode 5)': 'https://www.youtube.com/watch?v=pYWiLm_-sXw&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=5',
                      'Bob Ross - Secluded Beach (Season 9 Episode 6)': 'https://www.youtube.com/watch?v=WGUcw_kFvzU&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=6',
                      'Bob Ross - Forest Hills (Season 9 Episode 7)': 'https://www.youtube.com/watch?v=E3XW_Zp238U&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=7',
                      'Bob Ross - Little House by the Road (Season 9 Episode 8)': 'https://www.youtube.com/watch?v=3CDg_9gL-5M&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=8',
                      'Bob Ross - Mountain Path (Season 9 Episode 9)': 'https://www.youtube.com/watch?v=e0VUprkc1n0&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=9',
                      'Bob Ross - Country Charm (Season 9 Episode 10)': 'https://www.youtube.com/watch?v=9wp8NRzCJnw&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=10',
                      "Bob Ross - Nature's Paradise (Season 9 Episode 11)": 'https://www.youtube.com/watch?v=7yU55PUls2c&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=11',
                      'Bob Ross - Mountain by the Sea (Season 9 Episode 12)': 'https://www.youtube.com/watch?v=so--opB-yuQ&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=12',
                      'Bob Ross - Mountain Hideaway (Season 9 Episode 13)': 'https://www.youtube.com/watch?v=q48EWPrbzVs&list=PLAEQD0ULngi6eJ6Sry9JCR0afC1HEhMjo&index=13'},
                  'The Joy of Painting - Season 8': {
                      'Bob Ross - Misty Rolling Hills (Season 8 Episode 1)': 'https://www.youtube.com/watch?v=cC5ozePVKGI&index=1&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Lakeside Cabin (Season 8 Episode 2)': 'https://www.youtube.com/watch?v=CP6_5cQVZvQ&index=2&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Warm Winter Day (Season 8 Episode 3)': 'https://www.youtube.com/watch?v=mUJoNLWQ1yI&index=3&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Waterside Way (Season 8 Episode 4)': 'https://www.youtube.com/watch?v=uj5FE70BcB0&index=4&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      "Bob Ross - Hunter's Haven (Season 8 Episode 5)": 'https://www.youtube.com/watch?v=Da4SPyh1ATM&index=5&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Bubbling Mountain Brook (Season 8 Episode 6)': 'https://www.youtube.com/watch?v=U2_SKgM3f4A&index=6&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Winter Hideaway (Season 8 Episode 7)': 'https://www.youtube.com/watch?v=19oz9XHZNzA&index=7&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Foot of the Mountain (Season 8 Episode 8)': 'https://www.youtube.com/watch?v=cIUBUc_ITBc&index=8&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Majestic Pine (Season 8 Episode 9)': 'https://www.youtube.com/watch?v=x5CoQj9zr-c&index=9&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Cactus at Sunset (Season 8 Episode 10)': 'https://www.youtube.com/watch?v=XBqD3QhKU24&index=10&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Mountain Range (Season 8 Episode 11)': 'https://www.youtube.com/watch?v=V_l6olF3yHI&index=11&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Lonely Retreat (Season 8 Episode 12)': 'https://www.youtube.com/watch?v=qTDQt_PdlYc&index=12&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR',
                      'Bob Ross - Northern Lights (Season 8 Episode 13)': 'https://www.youtube.com/watch?v=vgbMONXc9Cs&index=13&list=PLAEQD0ULngi7_Td-kv4YRaDwJUpUuz0WR'},
                  'The Joy of Painting - Season 7': {
                      'Bob Ross - Winter Cabin (Season 7 Episode 1)': 'https://www.youtube.com/watch?v=kdlHV6ceI_g&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=1',
                      'Bob Ross - Secluded Lake (Season 7 Episode 2)': 'https://www.youtube.com/watch?v=2OxSJcFvpoU&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=2',
                      'Bob Ross - Evergreens at Sunset (Season 7 Episode 3)': 'https://www.youtube.com/watch?v=YQPEy3hYGo8&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=3',
                      'Bob Ross - Mountain Cabin (Season 7 Episode 4)': 'https://www.youtube.com/watch?v=E3IAMvO8GyM&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=4',
                      'Bob Ross - Portrait of Sally (Season 7 Episode 5)': 'https://www.youtube.com/watch?v=MHJB0IBnuD4&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=5',
                      'Bob Ross - Misty Waterfall (Season 7 Episode 6)': 'https://www.youtube.com/watch?v=530_cVmexiI&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=6',
                      'Bob Ross - Barn at Sunset (Season 7 Episode 7)': 'https://www.youtube.com/watch?v=WT6n0K2zGnA&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=7',
                      'Bob Ross - Mountain Splendor (Season 7 Episode 8)': 'https://www.youtube.com/watch?v=GhOGZMpPUSE&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=8',
                      'Bob Ross - Lake by Mountain (Season 7 Episode 9)': 'https://www.youtube.com/watch?v=yAiYirlcq7o&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=9',
                      'Bob Ross - Mountain Glory (Season 7 Episode 10)': 'https://www.youtube.com/watch?v=0M9pwLHRR2c&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=10',
                      'Bob Ross - Grey Winter (Season 7 Episode 11)': 'https://www.youtube.com/watch?v=sS-hNYgDUak&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=11',
                      'Bob Ross - Dock Scene (Season 7 Episode 12)': 'https://www.youtube.com/watch?v=4KYxkqlzyqM&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=12',
                      'Bob Ross - Dark Waterfall (Season 7 Episode 13)': 'https://www.youtube.com/watch?v=VqMbL00eZqw&list=PLAEQD0ULngi5oKehJMOnVTetKSjfmFrT1&index=13'},
                  'The Joy of Painting - Season 6': {
                      'Bob Ross - Blue River (Season 6 Episode 1)': 'https://www.youtube.com/watch?v=LygUyAb78oY&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=1',
                      "Bob Ross - Nature's Edge (Season 6 Episode 2)": 'https://www.youtube.com/watch?v=Bcqyzo85A1o&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=2',
                      'Bob Ross - Morning Mist (Season 6 Episode 3)': 'https://www.youtube.com/watch?v=wbZreRaE74k&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=3',
                      'Bob Ross - Whispering Stream (Season 6 Episode 4)': 'https://www.youtube.com/watch?v=QglIjlqsUdU&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=4',
                      'Bob Ross - Secluded Forest (Season 6 Episode 5)': 'https://www.youtube.com/watch?v=USkduOfwJok&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=5',
                      'Bob Ross - Snow Trail (Season 6 Episode 6)': 'https://www.youtube.com/watch?v=n9EsFFtwZnE&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=6',
                      'Bob Ross - Arctic Beauty (Season 6 Episode 7)': 'https://www.youtube.com/watch?v=UQ-RTZCOQn0&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=7',
                      'Bob Ross - Horizons West (Season 6 Episode 8)': 'https://www.youtube.com/watch?v=m6UM-rN2D6s&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=8',
                      'Bob Ross - High Chateau (Season 6 Episode 9)': 'https://www.youtube.com/watch?v=dafH8ks9Zww&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=9',
                      'Bob Ross - Country Life (Season 6 Episode 10)': 'https://www.youtube.com/watch?v=j8Jf7QVKLgQ&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=10',
                      'Bob Ross - Western Expanse (Season 6 Episode 11)': 'https://www.youtube.com/watch?v=MTInkV5ODjk&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=11',
                      'Bob Ross - Marshlands (Season 6 Episode 12)': 'https://www.youtube.com/watch?v=Ugiwi8uizpg&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=12',
                      'Bob Ross - Blaze of Color (Season 6 Episode 13)': 'https://www.youtube.com/watch?v=se7wOprxRGs&list=PLAEQD0ULngi5UR35RJsvL0Xvlm3oeY4Ma&index=13'},
                  'The Joy of Painting - Season 5': {
                      'Bob Ross - Mountain Waterfall (Season 5 Episode 1)': 'https://www.youtube.com/watch?v=DqhzxdkdQS0&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=1',
                      'Bob Ross - Twilight Meadow (Season 5 Episode 2)': 'https://www.youtube.com/watch?v=6evqNlOO7Bw&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=2',
                      'Bob Ross - Mountain Blossoms (Season 5 Episode 3)': 'https://www.youtube.com/watch?v=UVhhStJAJZc&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=3',
                      'Bob Ross - Winter Stillness (Season 5 Episode 4)': 'https://www.youtube.com/watch?v=qg9c1SqdRko&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=4',
                      'Bob Ross - Quiet Pond (Season 5 Episode 5)': 'https://www.youtube.com/watch?v=aiK9xOIJtV8&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=5',
                      'Bob Ross - Ocean Sunrise (Season 5 Episode 6)': 'https://www.youtube.com/watch?v=u0Bz6TNUK1Q&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=6',
                      'Bob Ross - Bubbling Brook (Season 5 Episode 7)': 'https://www.youtube.com/watch?v=LiKCzeqn-kg&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=7',
                      'Bob Ross - Arizona Splendor (Season 5 Episode 8)': 'https://www.youtube.com/watch?v=spFwCh2616s&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=8',
                      'Bob Ross - Anatomy of a Wave (Season 5 Episode 9)': 'https://www.youtube.com/watch?v=DFQlu6eqrBo&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=9',
                      'Bob Ross - The Windmill (Season 5 Episode 10)': 'https://www.youtube.com/watch?v=xj8xsTSkbUk&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=10',
                      'Bob Ross - Autumn Glory (Season 5 Episode 11)': 'https://www.youtube.com/watch?v=yTzlm_t0RmY&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=11',
                      'Bob Ross - Indian Girl (Season 5 Episode 12)': 'https://www.youtube.com/watch?v=2uXMx8Kjs8I&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=12',
                      'Bob Ross - Meadow Stream (Season 5 Episode 13)': 'https://www.youtube.com/watch?v=87MMbN1bQCs&list=PLAEQD0ULngi6bAFRfcqgpKP4T4SnoxoAz&index=13'},
                  'The Joy of Painting - Season 4': {
                      'Bob Ross - Purple Splendor (Season 4 Episode 1)': 'https://www.youtube.com/watch?v=hP4GfMgsNVE&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=1',
                      'Bob Ross - Tranquil Valley (Season 4 Episode 2)': 'https://www.youtube.com/watch?v=PbchoOWWCZs&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=2',
                      'Bob Ross - Majestic Mountains (Season 4 Episode 3)': 'https://www.youtube.com/watch?v=NcVeRlPu_5w&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=3',
                      'Bob Ross - Winter Sawscape (Season 4 Episode 4)': 'https://www.youtube.com/watch?v=lmKAwKrONmE&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=4',
                      'Bob Ross - Evening Seascape (Season 4 Episode 5)': 'https://www.youtube.com/watch?v=y5k4GXw_-yI&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=5',
                      'Bob Ross - Warm Summer Day (Season 4 Episode 6)': 'https://www.youtube.com/watch?v=GBN9AIw3Ao4&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=6',
                      'Bob Ross - Cabin in the Woods (Season 4 Episode 7)': 'https://www.youtube.com/watch?v=81QKellPA70&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=7',
                      'Bob Ross - Wetlands (Season 4 Episode 8)': 'https://www.youtube.com/watch?v=2FpVyGanPwM&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=8',
                      'Bob Ross - Cool Waters (Season 4 Episode 9)': 'https://www.youtube.com/watch?v=tJRvBcqQd5A&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=9',
                      'Bob Ross - Quiet Woods (Season 4 Episode 10)': 'https://www.youtube.com/watch?v=wIZX57I4aDs&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=10',
                      'Bob Ross - Northwest Majesty (Season 4 Episode 11)': 'https://www.youtube.com/watch?v=9DU6bunvD_g&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=11',
                      'Bob Ross - Autumn Days (Season 4 Episode 12)': 'https://www.youtube.com/watch?v=VAdMkf-AAPM&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=12',
                      'Bob Ross - Mountain Challenge (Season 4 Episode 13)': 'https://www.youtube.com/watch?v=o2cjLA_wgIk&list=PLAEQD0ULngi56KMlB1P_wK9pJZcMpEFQd&index=13'},
                  'The Joy of Painting - Season 3': {
                      'Bob Ross - Mountain Retreat (Season 3 Episode 1)': 'https://www.youtube.com/watch?v=hoimk4s8JoQ&index=1&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Blue Moon (Season 3 Episode 2)': 'https://www.youtube.com/watch?v=loit61vLUMc&index=2&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Bubbling Stream (Season 3 Episode 3)': 'https://www.youtube.com/watch?v=fuFalEXVN0k&index=3&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Winter Night (Season 3 Episode 4)': 'https://www.youtube.com/watch?v=8ysFkNYwhAE&index=4&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Distant Hills (Season 3 Episode 5)': 'https://www.youtube.com/watch?v=8Zge88tVwjE&index=5&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Covered Bridge (Season 3 Episode 6)': 'https://www.youtube.com/watch?v=OHSm8kLE7js&index=6&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Quiet Inlet (Season 3 Episode 7)': 'https://www.youtube.com/watch?v=9N5IWKzYIyU&index=7&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Night Light (Season 3 Episode 8)': 'https://www.youtube.com/watch?v=l141Y0x8om0&index=8&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - The Old Mill (Season 3 Episode 9)': 'https://www.youtube.com/watch?v=OFKFUJ9eDNs&index=9&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Campfire (Season 3 Episode 10)': 'https://www.youtube.com/watch?v=L5bXkI0-pEg&index=10&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Rustic Barn (Season 3 Episode 11)': 'https://www.youtube.com/watch?v=WJJwrnFhUUg&index=11&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Hidden Lake (Season 3 Episode 12)': 'https://www.youtube.com/watch?v=P_DaqkFbnac&index=12&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh',
                      'Bob Ross - Peaceful Waters (Season 3 Episode 13)': 'https://www.youtube.com/watch?v=Z0vtjRLqXcQ&index=13&list=PLAEQD0ULngi7zDD6O36FKkEHse-JCdVvh'},
                  'The Joy of Painting - Season 2': {
                      'Bob Ross - Meadow Lake (Season 2 Episode 1)': 'https://www.youtube.com/watch?v=GARWowi0QXI&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=1',
                      'Bob Ross - Winter Sun (Season 2 Episode 2)': 'https://www.youtube.com/watch?v=VPfYRj4DDco&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=2',
                      'Bob Ross - Ebony Sea (Season 2 Episode 3)': 'https://www.youtube.com/watch?v=aOJsKNzO3i8&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=3',
                      'Bob Ross - Shades of Grey (Season 2 Episode 4)': 'https://www.youtube.com/watch?v=I-ousb8-SD0&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=4',
                      'Bob Ross - Autumn Splendor (Season 2 Episode 5)': 'https://www.youtube.com/watch?v=rTTWw5Gd79I&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=5',
                      'Bob Ross - Black River (Season 2 Episode 6)': 'https://www.youtube.com/watch?v=6O4sfJd8G_M&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=6',
                      'Bob Ross - Brown Mountain (Season 2 Episode 7)': 'https://www.youtube.com/watch?v=Vx6v47gHBWM&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=7',
                      'Bob Ross - Reflections (Season 2 Episode 8)': 'https://www.youtube.com/watch?v=0FYfo94qefg&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=8',
                      'Bob Ross - Black and White Seascape (Season 2 Episode 9)': 'https://www.youtube.com/watch?v=PMDyPrE0puo&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=9',
                      'Bob Ross - Lazy River (Season 2 Episode 10)': 'https://www.youtube.com/watch?v=BW2wKKFvH1g&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=10',
                      'Bob Ross - Black Waterfall (Season 2 Episode 11)': 'https://www.youtube.com/watch?v=GzSqjyQUPZQ&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=11',
                      'Bob Ross - Mountain Waterfall (Season 2 Episode 12)': 'https://www.youtube.com/watch?v=9jIt95PCFAA&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=12',
                      'Bob Ross - Final Grace (Season 2 Episode 13)': 'https://www.youtube.com/watch?v=miJ19Kz_i3Y&list=PLAEQD0ULngi5VAEOviVE6svrUW2axISf6&index=13'},
'The Joy of Painting - Season 1': {'Bob Ross - A Walk in the Woods (Season 1 Episode 1)': 'https://www.youtube.com/watch?v=oh5p5f5_-7A&index=1&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Mt. McKinley (Season 1 Episode 2)': 'https://www.youtube.com/watch?v=RInDWhYceLU&index=2&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Ebony Sunset (Season 1 Episode 3)': 'https://www.youtube.com/watch?v=UOziR7PoVco&index=3&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Winter Mist (Season 1 Episode 4)': 'https://www.youtube.com/watch?v=0pwoixRikn4&index=4&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Quiet Stream (Season 1 Episode 5)': 'https://www.youtube.com/watch?v=DFSIQNjKRfk&index=5&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Winter Moon (Season 1 Episode 6)': 'https://www.youtube.com/watch?v=loAzRUzx1wI&index=6&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Autumn Mountain (Season 1 Episode 7)': 'https://www.youtube.com/watch?v=sDdpc8uisD0&index=7&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Peaceful Valley (Season 1 Episode 8)': 'https://www.youtube.com/watch?v=kQlFwTOkYzg&index=8&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Seascape (Season 1 Episode 9)': 'https://www.youtube.com/watch?v=QxcS7p1VHyQ&index=9&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Mountain Lake (Season 1 Episode 10)': 'https://www.youtube.com/watch?v=wDnLlywAL5I&index=10&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Winter Glow (Season 1 Episode 11)': 'https://www.youtube.com/watch?v=Q03YvknOVe0&index=11&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Snow Fall (Season 1 Episode 12)': 'https://www.youtube.com/watch?v=4E35-8x_y04&index=12&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu', 'Bob Ross - Final Reflections (Season 1 Episode 13)': 'https://www.youtube.com/watch?v=IEQWfszfRlA&index=13&list=PLAEQD0ULngi69x_7JbQvSMprLRK_KSVLu'},
}

missing = {'The Joy of Painting Season 8': {"Bob Ross - Bubbling Mountain Brook (Season 8 Episode 6)": "https://www.youtube.com/watch?v=U2_SKgM3f4A"},
           'The Joy of Painting Season 9': {"Bob Ross - Secluded Beach (Season 9 Episode 6)": "https://www.youtube.com/watch?v=WGUcw_kFvzU"},
           "The Joy of Painting Season 12": {"Bob Ross - Quiet Mountains River (Season 12 Episode 7)": "https://www.youtube.com/watch?v=Leiw-FtADZc&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=7",
                                             "Bob Ross - Soft Mountain Glow (Season 12 Episode 11)": "https://www.youtube.com/watch?v=gOGJYHWjXgE&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=11",
                                             "Bob Ross - Mountain in an Oval (Season 12 Episode 12)": "https://www.youtube.com/watch?v=1jRPshs27H8&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=12"},
            "The Joy of Painting Season 13": {"Bob Ross - Mountain Exhibition (Season 13 Episode 8)": "https://www.youtube.com/watch?v=bgI3_1quJ18&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=8"}
           }



for k, v in dutch.items():
    print(k + '---------')
    for k2, v2 in v.items():
        print(k2 + ': ' + v2)
    print('\n\n')
scrape(dutch)



"""scrape({"season1": {"episode1": "https://www.youtube.com/watch?v=wdr4t7cQW2U"},
       "season2": {"episode1": "https://www.youtube.com/watch?v=GARWowi0QXI",
                   "epi2": "https://www.youtube.com/watch?v=VPfYRj4DDco"}})"""

