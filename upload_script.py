from mutagen.easyid3 import EasyID3
import os
import requests
import json

def get_artists(audiopath):
    try:
        id3 = EasyID3(audiopath)
        artists = id3.get("artist", [])
        normalized_artists = [artist.lower().decode("utf8") for artist in artists]
        return normalized_artists
    except:
        return []

def collect_artists(musicdirs):
    all_artists = set()
    for musicdir in musicdirs:
        print "Reading {}...".format(musicdir)
        for root, _, files in os.walk(musicdir):
            for audiopath in files:
                audiopath = os.path.join(root, audiopath)
                artists = get_artists(audiopath)
                all_artists.update(artists)
        print "Done."
    return all_artists

def upload_artists(artists):
    print "Uploading artists..."
    api_call = "http://127.0.0.1:8000/pyconcert/upload"
    artists = list(artists)
    requests.post(api_call, data={'artists':json.dumps(artists)})
    print "Done."

def existing_dir(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError("Path does not exist: {}".format(path))
    return path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload local artists to pyconcert')
    parser.add_argument('musicdirs', metavar='musicdirs', type=existing_dir, nargs="+",
                        help='Directories to search.')
            
    args = parser.parse_args()
    artists = collect_artists(args.musicdirs)
    print "Found {} artists.".format(len(artists))
    # upload_artists(artists)
    artists = list(artists)
    with open("out.json", "w") as json_file: 
        json.dump(artists, json_file)