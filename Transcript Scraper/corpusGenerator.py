import os

transcripts = []

for root, dirs, files in os.walk(r".\Transcripts"):
    for file in files:
        if file.startswith("Bob Ross -") and file.endswith(".txt"):
            transcripts.append(os.path.join(root, file))
count = 0
with open('RossCorpusCleaned.txt', 'wb') as outfile:
    for filename in transcripts:
        with open(filename, 'rb') as infile:
            for line in infile:
                outfile.write(line)
                count += 1
print(count)
print(transcripts)
print(len(transcripts))



