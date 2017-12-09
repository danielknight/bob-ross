import string
import os
import regex as re
import collections
dir = os.path.dirname(__file__)


def remove_punctuation(text):
    pat = re.compile(b'\p{P}+')
    return re.sub(pat, "", text)


def replace_nl_with_space(text):
    pat = re.compile(b'\n')
    return re.sub(pat, b" ", text)



paints = ['Phthalo Blue', 'Van Dyke Brown', 'Black', 'Alizarin Crimson', 'Midnight Black', 'Bright Red',
          'Phthalo Green', 'Cadmium Yellow', 'Dark Sienna', 'Mountain Mixture', 'Prussian Blue', 'Indian Yellow',
          'Sap Green', 'Titanium White', 'Magic White', 'Yellow Ochre', 'Thalo Blue', 'Thalo Green', 'Cad Yellow',
          'Russian Blue', 'Crimson', 'Liquid Black', 'Liquid White', 'Liquid Clear', 'Indian Red', 'Black Gesso', 'Permanent Red' ]

paints_dict = {
    'Phthalo Blue': ['http://amzn.to/2tV2Iee',
                     """<a target="_blank" href="https://www.amazon.com/gp/product/B0009IL2N2/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0009IL2N2&linkCode=as2&tag=happylittletr-20&linkId=9c88b153936c5921f78e84f064e19d6f">Winton Oil Paint 37ml Tube: Phthalo Blue</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0009IL2N2" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Van Dyke Brown': ['http://amzn.to/2sYpBNW',
                       """<a target="_blank" href="https://www.amazon.com/gp/product/B004O7BQF8/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B004O7BQF8&linkCode=as2&tag=happylittletr-20&linkId=e2cc7b132f02774b8aa23bdcc55f2745">Winton Oil Paint 37ml/Tube-Vandyke Brown</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B004O7BQF8" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Alizarin Crimson': ['http://amzn.to/2tlQbDK',
                         """<a target="_blank" href="https://www.amazon.com/gp/product/B004O79MIQ/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B004O79MIQ&linkCode=as2&tag=happylittletr-20&linkId=8580e892cd9ad9100cea24434c338a0a">Winton Oil Paint 37ml/Tube-Permanent Alizarin Crimson</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B004O79MIQ" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Midnight Black': ['http://amzn.to/2ufBL4q',
                       """<a target="_blank" href="https://www.amazon.com/gp/product/B0027AEEB2/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0027AEEB2&linkCode=as2&tag=happylittletr-20&linkId=987f5f4313abbfdd58a22edb3f2662b2">Bob Ross MR6004 37-Ml Artist Oil Color, Midnight Black</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0027AEEB2" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Bright Red': ['http://amzn.to/2tlCEvQ',
                   """<a target="_blank" href="https://www.amazon.com/gp/product/B001E1TGHW/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B001E1TGHW&linkCode=as2&tag=happylittletr-20&linkId=3581088b6e63dbfa3a3a74332d38f3ad">Winsor &amp; Newton Artists Oil Color Paint Tube, 37ml, Bright Red</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B001E1TGHW" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Phthalo Green': ['http://amzn.to/2sYGFn8',
                      """<a target="_blank" href="https://www.amazon.com/gp/product/B001JPIQ2O/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B001JPIQ2O&linkCode=as2&tag=happylittletr-20&linkId=201795ad28afca3898f835fb3540b703">M. Graham Artist Oil Paint Phthalo Green 1.25oz/37ml Tube</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B001JPIQ2O" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Cadmium Yellow': ['http://amzn.to/2tVdWPX',
                       """<a target="_blank" href="https://www.amazon.com/gp/product/B0009IL2JG/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0009IL2JG&linkCode=as2&tag=happylittletr-20&linkId=1d4e4ce111220c9076059a038543f8d8">Winsor &amp; Newton Winton 37-Milliliter Oil Paint, Cadmium Yellow Light</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0009IL2JG" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Dark Sienna': ['http://amzn.to/2rZwQ76',
                    """<a target="_blank" href="https://www.amazon.com/gp/product/B0027A3G4S/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0027A3G4S&linkCode=as2&tag=happylittletr-20&linkId=f2c5fde46159db0b7d8eda05c22413f8">Bob Ross MR6001 37-Ml Artist Oil Color, Dark Sienna</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0027A3G4S" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Mountain Mixture': ['http://amzn.to/2rZ93nK',
                         """<a target="_blank" href="https://www.amazon.com/gp/product/B0027IUSF0/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0027IUSF0&linkCode=as2&tag=happylittletr-20&linkId=748d93b215527ece07eb14813d0cfbaa">Bob Ross MR6020 37-Ml Artist Oil Color, Mountain Mixture</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0027IUSF0" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Prussian Blue': ['http://amzn.to/2tlzUyB',
                      """<a target="_blank" href="https://www.amazon.com/gp/product/B004O79Q3C/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B004O79Q3C&linkCode=as2&tag=happylittletr-20&linkId=837f1c395a2c078caf3812a37b9d42fe">Winton Oil Paint 37ml/Tube-Prussian Blue</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B004O79Q3C" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Indian Yellow': ['http://amzn.to/2tilqPm',
                      """<a target="_blank" href="https://www.amazon.com/gp/product/B0027AEEGC/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0027AEEGC&linkCode=as2&tag=happylittletr-20&linkId=d4b729bf567017814054f00b086252aa">Bob Ross MR6070 37-Ml Artist Oil Color, Indian Yellow</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0027AEEGC" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Sap Green': ['http://amzn.to/2tVmjuW',
                  """<a target="_blank" href="https://www.amazon.com/gp/product/B0052XYDIU/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0052XYDIU&linkCode=as2&tag=happylittletr-20&linkId=5f8fc03d6ecde9201853414e9b6a4ff0">Winsor &amp; Newton Winton Oil Colour Tube, 37ml, Sap Green</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0052XYDIU" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Titanium White': ['http://amzn.to/2sYIQH2',
                       """<a target="_blank" href="https://www.amazon.com/gp/product/B0044JPSDW/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0044JPSDW&linkCode=as2&tag=happylittletr-20&linkId=85cd12fe1d08ab8097d42b3bbff66971">Winsor &amp; Newton Winton 200-Milliliter Oil Paint, Titanium White</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0044JPSDW" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Magic White': ['http://amzn.to/2sk2uLL',
                    """<a target="_blank" href="https://www.amazon.com/gp/product/B0027A3F6W/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0027A3F6W&linkCode=as2&tag=happylittletr-20&linkId=9cac9076701d57d506089efe2d8dbf0f">Martin/ F. Weber Bob Ross 236-Ml Oil Paint, Liquid White</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0027A3F6W" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Yellow Ochre': ['http://amzn.to/2sk2H1v',
                     """<a target="_blank" href="https://www.amazon.com/gp/product/B004IXDHNM/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B004IXDHNM&linkCode=as2&tag=happylittletr-20&linkId=aaa0950e553ef4aaba6b3db266b8a7ea">Winsor &amp; Newton Winton Oil Colour Tube, 37ml, Yellow Ochre</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B004IXDHNM" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Thalo Blue': ['http://amzn.to/2tV2Iee',
                   """<a target="_blank" href="https://www.amazon.com/gp/product/B0009IL2N2/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0009IL2N2&linkCode=as2&tag=happylittletr-20&linkId=9c88b153936c5921f78e84f064e19d6f">Winton Oil Paint 37ml Tube: Phthalo Blue</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0009IL2N2" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Thalo Green': ['http://amzn.to/2sYGFn8',
                    """<a target="_blank" href="https://www.amazon.com/gp/product/B001JPIQ2O/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B001JPIQ2O&linkCode=as2&tag=happylittletr-20&linkId=201795ad28afca3898f835fb3540b703">M. Graham Artist Oil Paint Phthalo Green 1.25oz/37ml Tube</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B001JPIQ2O" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Cad Yellow': ['http://amzn.to/2tVdWPX',
                   """<a target="_blank" href="https://www.amazon.com/gp/product/B0009IL2JG/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B0009IL2JG&linkCode=as2&tag=happylittletr-20&linkId=1d4e4ce111220c9076059a038543f8d8">Winsor &amp; Newton Winton 37-Milliliter Oil Paint, Cadmium Yellow Light</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B0009IL2JG" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Russian Blue': ['http://amzn.to/2tlzUyB',
                     """<a target="_blank" href="https://www.amazon.com/gp/product/B004O79Q3C/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B004O79Q3C&linkCode=as2&tag=happylittletr-20&linkId=837f1c395a2c078caf3812a37b9d42fe">Winton Oil Paint 37ml/Tube-Prussian Blue</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B004O79Q3C" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Crimson': ['http://amzn.to/2tlQbDK',
                """<a target="_blank" href="https://www.amazon.com/gp/product/B004O79MIQ/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B004O79MIQ&linkCode=as2&tag=happylittletr-20&linkId=8580e892cd9ad9100cea24434c338a0a">Winton Oil Paint 37ml/Tube-Permanent Alizarin Crimson</a><img src="//ir-na.amazon-adsystem.com/e/ir?t=happylittletr-20&l=am2&o=1&a=B004O79MIQ" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />"""],
    'Liquid White': [],
    'Liquid Black': [],
    'Black Gesso': [],
    'Liquid Clear': []
}

paints = [paint.replace(' ', '\n').upper().encode('utf-8') for paint in paints]
print(paints)

transcripts = []


def fcount(path, map={}):
    count = 0
    for f in os.listdir(path):
        child = os.path.join(path, f)
        if os.path.isdir(child):
            child_count = fcount(child, map)
            count += child_count + 1
    map[path] = count
    return count

def replace(colors):
    color_map = {'CRIMSON': 'ALIZARIN CRIMSON',
                 'THALO GREEN': 'PHTHALO GREEN',
                 'THALO BLUE': 'PHTHALO BLUE',
                 'PTHALO GREEN': 'PHTHALO GREEN',
                 'PERMANENT RED': 'PERMANENT RED',
                 'CAD YELLOW': 'CADMIUM YELLOW',
                 'RUSSIAN BLUE': 'PRUSIAN BLUE',
                 'PRUSSIAN BLUE': 'PRUSIAN BLUE',
                 'PTHALO BLUE': 'PHTHALO BLUE',
                 'BLACK': 'MIDNIGHT BLACK',
                 'MAGIC WHITE': 'LIQUID WHITE'}

    for falsecolor, truecolor in color_map.items():
        if falsecolor in colors:
            colors[colors.index(falsecolor)] = truecolor


for root, dirs, files in os.walk(r".\Transcripts"):
    for file in files:
        if file.endswith(".txt") and not file in ["data.txt", "paint.txt"]:
                transcripts.append(os.path.join(root, file))

paint_dict = {}
for filename in transcripts:
    with open(filename, 'rb') as infile:
        episode_text = remove_punctuation(infile.read().upper())
        episode_text = episode_text.decode('utf8')
        colors = [replace_nl_with_space(color).decode('utf-8') for color in paints if color.decode('utf8') in episode_text]
        print(colors)
        replace(colors)
        color_count = {}
        print(colors, filename)
        for c in set(colors):
            color_count[c] = episode_text.count(c.replace(' ', '\n'))
        print(color_count)
        print('\n')
        paint_dict[filename] = colors

"""for root, dirs, files in os.walk(r".\Transcripts"):
    for dirname in dirs:
        c = fcount(os.path.join(dir, 'Transcripts', dirname))
        print(c, " in season %s" % dirname.split()[-1])"""

"""for k, v in paint_dict.items():
    print(k + '---------')
    data_path = os.path.join(os.path.dirname(k), 'paint.txt')
    print(data_path)
    print(v)
    print('\n\n')
    with open(data_path, 'w') as f:
        paints = "\n".join(v)
        paints += '\n'
        f.writelines(paints)"""

print(len(paint_dict))
print(len(transcripts))

