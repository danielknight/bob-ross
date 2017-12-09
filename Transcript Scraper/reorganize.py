import os
from shutil import move


for root, dirs, files in os.walk(r".\Transcripts\The Joy of Painting - Season 1", topdown=False):
    for file in files:
        if file.endswith(".txt"):
            episode_name = os.path.splitext(file)[0]
            os.makedirs(os.path.join(root, episode_name), exist_ok=True)
            move(os.path.join(root, file), os.path.join(root, episode_name, file))
