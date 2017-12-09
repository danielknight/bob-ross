
"""Make a wordcloud from the Bob Ross Corpus
"""

from os import path
from os import walk
from wordcloud import WordCloud
import matplotlib.pyplot as plt

transcripts = []
for root, dirs, files in walk(r".\Transcripts\The Joy of Painting - Season 1"):
    for file in files:
        if file.endswith(").txt"):
            episode_name = path.splitext(file)[0]
            text = open(path.join(root, file)).read()

            # Read the whole text.
            # text = open(path.join(d, 'Transcripts', 'The Joy of Painting - Season 2', 'Bob Ross - Autumn Splendor (Season 2 Episode 5).txt')).read()
            # text = open(path.join(d, 'RossCorpus.txt')).read()
            # Generate a word cloud image
            wordcloud = WordCloud(collocations=False).generate(text)
            # Display the generated image:
            # the matplotlib way:
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.imsave(path.join(root, episode_name + '.png'), wordcloud)
            # lower max_font_size
            wordcloud = WordCloud(max_font_size=40, collocations=False).generate(text)
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.imsave(path.join(root, episode_name + "_max_font_40.png"), wordcloud)
            #input("any key to continue...")
#d = path.dirname(path.abspath(__file__)) #get the current directory

