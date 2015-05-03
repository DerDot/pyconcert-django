from mutagen.easyid3 import EasyID3
import os
import json
import webbrowser

def get_artists(audiopath):
    try:
        id3 = EasyID3(audiopath)
        artists = id3.get("artist", [])
        normalized_artists = [artist.lower().decode("utf8") for artist in artists]
        return normalized_artists
    except:
        return []
    
def get_first_level(top, current):
    rel = os.path.relpath(current, top)
    return rel.split(os.sep)[0]

def print_first_level(top, current):
    first_level = get_first_level(top, current)
    if print_first_level.last != first_level:
        print "Searching in '{}'...".format(first_level)
        print_first_level.last = first_level
print_first_level.last = None

def collect_artists(musicdirs):
    all_artists = set()
    for musicdir in musicdirs:
        print "Reading {}...".format(musicdir)
        for root, _, files in os.walk(musicdir):
            print_first_level(musicdir, root)
            for audiopath in files:
                audiopath = os.path.join(root, audiopath)
                artists = get_artists(audiopath)
                all_artists.update(artists)
        print "Done."
    return all_artists

def upload_artists():
    url = "http://ec2-54-148-190-69.us-west-2.compute.amazonaws.com:8000/upload_json"
    webbrowser.open(url)

def existing_dir(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError("Path does not exist: {}".format(path))
    return path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload local artists to pyconcert')
    parser.add_argument('musicdirs', metavar='musicdirs', type=existing_dir, nargs="+",
                        help='Directories to search.')
    parser.add_argument('targetdir', metavar='targetdir', type=existing_dir, nargs="?",
                        default=".", help='Directory to write the result file to.')
            
    args = parser.parse_args()
    artists = collect_artists(args.musicdirs)
    print "Found {} artists.".format(len(artists))
    artists = list(artists)
    targetpath = os.path.join(args.targetdir, "local_artists.json")
    with open(targetpath, "w") as json_file: 
        json.dump(artists, json_file)
    upload_artists()