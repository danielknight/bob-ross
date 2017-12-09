import os

missing = {'The Joy of Painting - Season 8': {"Bob Ross - Bubbling Mountain Brook (Season 8 Episode 6)": "https://www.youtube.com/watch?v=U2_SKgM3f4A"},
           'The Joy of Painting - Season 9': {"Bob Ross - Secluded Beach (Season 9 Episode 6)": "https://www.youtube.com/watch?v=WGUcw_kFvzU"},
           "The Joy of Painting - Season 12": {"Bob Ross - Quiet Mountains River (Season 12 Episode 7)": "https://www.youtube.com/watch?v=Leiw-FtADZc&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=7",
                                             "Bob Ross - Soft Mountain Glow (Season 12 Episode 11)": "https://www.youtube.com/watch?v=gOGJYHWjXgE&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=11",
                                             "Bob Ross - Mountain in an Oval (Season 12 Episode 12)": "https://www.youtube.com/watch?v=1jRPshs27H8&list=PLAEQD0ULngi5d5K57ImROanUMpcF-HXIS&index=12"},
            "The Joy of Painting - Season 13": {"Bob Ross - Mountain Exhibition (Season 13 Episode 8)": "https://www.youtube.com/watch?v=bgI3_1quJ18&list=PLAEQD0ULngi5rdYozRhnJIOp5pWHCsPn2&index=8"}
           }
def write_empty(outfile):
    with open(outfile, "wb") as f:
        f.write('Unavailable'.encode("utf8"))


def handle(video_dict):
    if not os.path.exists('Transcripts'):
        os.makedirs('Transcripts')
    os.chdir('Transcripts')
    print(os.getcwd())
    #add folders for the missing episodes and write empty transcripts
    for season, season_dict in video_dict.items():
        if not os.path.exists(season):
            os.makedirs(season)
        os.chdir(season)
        cwd = os.getcwd()
        for episode_title, link in season_dict.items():
            if not os.path.exists(episode_title):
                os.makedirs(episode_title)
                os.chdir(episode_title)
                if not os.path.exists(episode_title+'.txt'):
                    write_empty(episode_title+'.txt')
                os.chdir('..')
        os.chdir('..')
handle(missing)