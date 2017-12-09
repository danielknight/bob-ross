import os
import string
import regex as re
import collections
dir = os.path.dirname(__file__)

transcripts = [r"C:\Users\Danny\PycharmProjects\BobRoss\Transcript Scraper\Transcripts\The Joy of Painting - Season 1\Bob Ross - Autumn Mountain (Season 1 Episode 7)\Bob Ross - Autumn Mountain (Season 1 Episode 7).txt"]
transcripts = []
def remove_punctuation(text):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    return regex.sub('', text)


def replace_nl_with_space(text):
    pat = re.compile(b'\n')
    return re.sub(pat, b" ", text)

def replace(transcripts):
    color_map = {#'CRIMSON': 'ALIZARIN CRIMSON',
                 'THALO GREEN': 'PHTHALO GREEN',
                 'THALO BLUE': 'PHTHALO BLUE',
                 'PTHALO GREEN': 'PHTHALO GREEN',
                 'PERMANENT RED': 'PERMANENT RED',
                 'CAD YELLOW': 'CADMIUM YELLOW',
                 'RUSSIAN BLUE': 'PRUSIAN BLUE',
                 'PRUSSIAN BLUE': 'PRUSIAN BLUE',
                 'PTHALO BLUE': 'PHTHALO BLUE',
                 'BLACK': 'MIDNIGHT BLACK',
                 'MAGIC WHITE': 'LIQUID WHITE',
                 'VAN DYCK BROWN': 'VAN DYKE BROWN',
                 'DYCK': 'DYKE'}
    pattern = re.compile('.*Bob Ross - (.*)\.txt$')
    for filename in transcripts:
        with open(filename, 'r+b') as infile:
            episode_text = remove_punctuation(infile.read().upper().decode('utf8'))
            episode_text = episode_text.replace('\n', ' ')

            for falsecolor, truecolor in color_map.items():
                if falsecolor in episode_text:
                    print(falsecolor + "found in episode")
                episode_text = episode_text.replace(falsecolor, truecolor)
            episode_text = episode_text.replace(' ', '\n')
            infile.seek(0)
            infile.write(episode_text.encode('utf8'))
            print("corrected: " + pattern.match(filename)[1])

for root, dirs, files in os.walk(r".\Transcripts"):
    for file in files:
        if file.endswith(".txt") and file not in ["data.txt", "paint.txt"]:
                transcripts.append(os.path.join(root, file))
replace(transcripts)




# read the file into a string, replace the typo words with the real words
