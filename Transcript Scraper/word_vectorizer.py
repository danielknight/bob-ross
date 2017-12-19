import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot as plt

import matplotlib as mpl
from sklearn.manifold import MDS
from sklearn.externals import joblib
import numpy as np
import pandas as pd
import time
import nltk
import re
import os
import codecs
from sklearn import feature_extraction
import mpld3
dir = os.path.dirname(__file__)

file_paths = [r'C:\Users\Danny\PycharmProjects\BobRoss\Transcript Scraper\Transcripts\The Joy of Painting - Season 1\Bob Ross - Autumn Mountain (Season 1 Episode 7)\Bob Ross - Autumn Mountain (Season 1 Episode 7).txt',
               r'C:\Users\Danny\PycharmProjects\BobRoss\Transcript Scraper\Transcripts\The Joy of Painting - Season 1\Bob Ross - A Walk in the Woods (Season 1 Episode 1)\Bob Ross - A Walk in the Woods (Season 1 Episode 1).txt']
file_paths = []
transcripts = []
titles = []
stopwords = nltk.corpus.stopwords.words('english')

# load nltk's SnowballStemmer as variabled 'stemmer'
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
stopwords.extend(['little', 'coat', 'shoot','ol','sorta', 'odorless', 'em', 'wan', 'wan na', 'yeah', 'something'])
# here I define a tokenizer and stemmer which returns the set of stems in the text that it is passed

def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token) and token not in stopwords:
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems


def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token) and token not in stopwords:
            filtered_tokens.append(token)
    return filtered_tokens


# not super pythonic, no, not at all.
# use extend so it's a big flat list of vocab
pattern = re.compile('Bob Ross - (.*)\.txt$')
for root, dirs, files in os.walk(r".\Transcripts"):
    for file in files:
        if file.endswith(".txt") and file not in ["data.txt", "paint.txt"]:
            f = os.path.join(root, file)
            file_paths.append(f)
            titles.append(pattern.match(file)[1])

totalvocab_stemmed = []
totalvocab_tokenized = []
for file in file_paths:
    with open(file, 'rb') as infile:
        text = infile.read().decode('utf8')
        transcripts.append(text)

for transcript in transcripts:
    allwords_stemmed = tokenize_and_stem(transcript)  # for each item in transcripts, tokenize/stem
    totalvocab_stemmed.extend(allwords_stemmed)  # extend the 'totalvocab_stemmed' list
    allwords_tokenized = tokenize_only(transcript)
    totalvocab_tokenized.extend(allwords_tokenized)

vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index=totalvocab_stemmed)
print('there are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame')
print(vocab_frame.head())

# gets us a vocab for the entire corpus and then we need to create a Term Freq Inverse Document Frequency Matrx
#       epi_1 -- epi_2
#word1  x           y
#word2  z           u

# use the tfidf to do some clustering, maybe k means
from sklearn.feature_extraction.text import TfidfVectorizer

#define vectorizer parameters
tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                 min_df=0.2, stop_words='english',
                                 use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))

joblib.dump(tfidf_vectorizer, 'vectorizer.pkl')
tfidf_vectorizer = joblib.load('vectorizer.pkl')

start = time.time()
tfidf_matrix = tfidf_vectorizer.fit_transform(transcripts) #fit the vectorizer to synopses
end = time.time()
print("Timing was: " + str(end-start))
print(tfidf_matrix.shape)

terms = tfidf_vectorizer.get_feature_names()
from sklearn.metrics.pairwise import cosine_similarity
dist = 1 - cosine_similarity(tfidf_matrix)
print(dist)


from sklearn.cluster import KMeans

num_clusters = 7

km = KMeans(n_clusters=num_clusters)

start = time.time()
km.fit(tfidf_matrix)
end = time.time()
print("Timing was: " + str(end-start))

clusters = km.labels_.tolist()


#uncomment the below to save your model
#since I've already run my model I am loading from the pickle

joblib.dump(km,  'doc_cluster.pkl')

km = joblib.load('doc_cluster.pkl')
clusters = km.labels_.tolist()


episodes = {'title': titles, 'transcript': transcripts, 'cluster': clusters}

frame = pd.DataFrame(episodes, index = [clusters], columns = ['title', 'cluster'])

frame['cluster'].value_counts() #number of films per cluster (clusters from 0 to 4)
print()
print("Top terms per cluster:")
print()
# sort cluster centers by proximity to centroid
order_centroids = km.cluster_centers_.argsort()[:, ::-1]

for i in range(num_clusters):
    print("Cluster %d words:" % i, end='')
    for ind in order_centroids[i, :6]:  # replace 6 with n words per cluster
        print(' %s' % vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'), end=',')
    print()  # add whitespace
    print()  # add whitespace

    print("Cluster %d titles:" % i, end='')
    for title in frame.ix[[i]]['title'].values.tolist():
        print(' %s,' % title, end='')
    print()  # add whitespace
    print()  # add whitespace

print()
print()


MDS()

# convert two components as we're plotting points in a two-dimensional plane
# "precomputed" because we provide a distance matrix
# we will also specify `random_state` so the plot is reproducible.
mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)

pos = mds.fit_transform(dist)  # shape (n_components, n_samples)

xs, ys = pos[:, 0], pos[:, 1]
print()
print()

#set up colors per clusters using a dict
cluster_colors_all = {0: '#98C829',
 1: '#1ADC81',
 2: '#6F1E11',
 3: '#2A240E',
 4: '#076DFE',
 5: '#BBD357',
 6: '#93F867',
 7: '#5FB4DA',
 8: '#9E8B51',
 9: '#D7ECDD',
 10: '#AE5F01',
 11: '#FF990F',
 12: '#6EDDEE',
 13: '#590253',
 14: '#BDE1D5',
 15: '#803CC7',
 16: '#7821E5',
 17: '#F8279E',
 18: '#4FF812',
 19: '#0AD333'}

cluster_colors = {k: cluster_colors_all[k] for k in range(num_clusters)}

#set up cluster names using a dict
cluster_names = {key: "TBD" for key in range(num_clusters)}

# create data frame that has the result of the MDS plus the cluster numbers and titles
df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=titles))

# group by cluster
groups = df.groupby('label')

# set up plot
fig, ax = plt.subplots(figsize=(17, 9))  # set size
ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling

# iterate through groups to layer the plot
# note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return the appropriate color/label
for name, group in groups:
    ax.plot(group.x, group.y, marker='o', linestyle='', ms=12,
            label=cluster_names[name], color=cluster_colors[name],
            mec='none')
    ax.set_aspect('auto')
    ax.tick_params( \
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelbottom='off')
    ax.tick_params( \
        axis='y',  # changes apply to the y-axis
        which='both',  # both major and minor ticks are affected
        left='off',  # ticks along the bottom edge are off
        top='off',  # ticks along the top edge are off
        labelleft='off')

ax.legend(numpoints=1)  # show legend with only 1 point

# add label in x,y position with the label as the film title
for i in range(len(df)):
    ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['title'], size=8)

plt.show()  # show the plot


# javascript plot
class TopToolbar(mpld3.plugins.PluginBase):
    """Plugin for moving toolbar to top of figure"""

    JAVASCRIPT = """
    mpld3.register_plugin("toptoolbar", TopToolbar);
    TopToolbar.prototype = Object.create(mpld3.Plugin.prototype);
    TopToolbar.prototype.constructor = TopToolbar;
    function TopToolbar(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    TopToolbar.prototype.draw = function(){
      // the toolbar svg doesn't exist
      // yet, so first draw it
      this.fig.toolbar.draw();

      // then change the y position to be
      // at the top of the figure
      this.fig.toolbar.toolbar.attr("x", 150);
      this.fig.toolbar.toolbar.attr("y", 400);

      // then remove the draw function,
      // so that it is not called again
      this.fig.toolbar.draw = function() {}
    }
    """
    def __init__(self):
        self.dict_ = {"type": "toptoolbar"}

# create data frame that has the result of the MDS plus the cluster numbers and titles
df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, title=titles))

# group by cluster
groups = df.groupby('label')

# define custom css to format the font and to remove the axis labeling
css = """
text.mpld3-text, div.mpld3-tooltip {
  font-family:Arial, Helvetica, sans-serif;
}

g.mpld3-xaxis, g.mpld3-yaxis {
display: none; }

svg.mpld3-figure {
margin-left: -200px;}
"""

# Plot
fig, ax = plt.subplots(figsize=(14, 6))  # set plot size
ax.margins(0.03)  # Optional, just adds 5% padding to the autoscaling

# iterate through groups to layer the plot
# note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return the appropriate color/label
for name, group in groups:
    points = ax.plot(group.x, group.y, marker='o', linestyle='', ms=18,
                     label=cluster_names[name], mec='none',
                     color=cluster_colors[name])
    ax.set_aspect('auto')
    labels = [i for i in group.title]

    # set tooltip using points, labels and the already defined 'css'
    tooltip = mpld3.plugins.PointHTMLTooltip(points[0], labels,
                                             voffset=10, hoffset=10, css=css)
    # connect tooltip to fig
    mpld3.plugins.connect(fig, tooltip, TopToolbar())

    # set tick marks as blank
    ax.axes.get_xaxis().set_ticks([])
    ax.axes.get_yaxis().set_ticks([])

    # set axis as blank
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)

ax.legend(numpoints=1)  # show legend with only one dot

mpld3.show()  # show the plot

# uncomment the below to export to html
html = mpld3.fig_to_html(fig)
print(html)

