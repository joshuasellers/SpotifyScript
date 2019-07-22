##################################
# Script for accessing a user's  #
# Spotify account and removing   #
# duplicate songs from their     #
# playlists                      #
##################################

import spotipy
from config import token, username


def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


def get_playlists(spotify):
    r = []
    empty = False
    offset = 0
    while not empty:
        result = spotify.current_user_playlists(limit=50, offset=offset)
        offset += 50
        if len(result['items']) == 0:
            empty = True
        else:
            r += result['items']
    return r


def get_tracks(spotify, playlist):
    tracks = []
    empty = False
    offset = 0
    while not empty:
        result = spotify.user_playlist_tracks(username,playlist,fields=None,limit=100,offset=offset,market=None)
        offset += 50
        if len(result['items']) == 0:
            empty = True
        elif len(result['items']) < 50:
            tracks += result['items']
            empty = True
        else:
            tracks += result['items']
    track_tracker = {}
    for track in tracks:
        if track['track']['id'] in track_tracker:
            track_tracker[track['track']['id']] += 1
        else:
            track_tracker[track['track']['id']] = 1
    for track in track_tracker:
        if track_tracker[track] == 1:
            track_tracker = removekey(track_tracker,track)
    removable_tracks = {}
    for track in track_tracker:
        count = track_tracker[track]
        for song in range(0,len(tracks)):
            if tracks[song]['track']['id'] == track:
                if count != 1:
                    count -= 1
                    if track not in removable_tracks:
                        removable_tracks[(tracks[song]['track']['name'],track)] = [[song]]
                    else:
                        removable_tracks[(tracks[song]['track']['name'],track)].append([song])
    return build_track_objects(removable_tracks)


def build_track_objects(tracks):
    objects = []
    for track in tracks:
        indices = [i[0] for i in tracks[track]]
        obj = {"uri": track[1], "positions": indices}
        objects.append((track[0], obj))
    return objects


def remove_dupes(duplicates, sp, playlist_id):
    for dupe in duplicates:
        obj = dupe[1]
        sp.user_playlist_remove_specific_occurrences_of_tracks(username,playlist_id,obj)



def script():
    if token and username:
        sp = spotipy.Spotify(auth=token)
        results = get_playlists(sp)
        for item in results:
            if item['owner']['id'] == username:
                playlist_id = item['id']
                playlist_name = item['name']
                dupes = get_tracks(sp, item['id'])

                print('************************')
                print(playlist_name)
                print(playlist_id)
                print("")
                print("Duplicates: ", dupes)
                remove_dupes(dupes, sp, playlist_id)
                print("")
                print("Duplicates removed")
                print('************************')
    else:
        print("Can't get token or username")


script()


