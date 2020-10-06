#!/usr/bin/env python3
"""Converts an iTunes library XML to a Rhythmbox library XML.
Writes output to stdout."""

import argparse
import logging
from lxml import etree
from os.path import expanduser
from urllib.parse import quote

from utils import DEFAULT_ITUNES_LIB_PATH, DEFAULT_ITUNES_MUSIC_ROOT, DEFAULT_RHYTHMBOX_MUSIC_ROOT, DEFAULT_RHYTHMBOX_PLAYLIST_PATH, get_itunes_library, warn_invalid_track, write_xml_to_file

IGNORED_PLAYLISTS = {"Library", "Music", "Movies", "TV Shows", "Purchased", "iTunes DJ", "Podcasts", "Mediathek", "Musik", "Filme", "TV-Sendungen", "iTunes U", "Bücher", "Töne", "Genius"}


def main() -> None:
    parser = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--itunes-lib-path', default = DEFAULT_ITUNES_LIB_PATH, help = 'path to iTunes library XML')
    parser.add_argument('--itunes-music-root', default = DEFAULT_ITUNES_MUSIC_ROOT, help = 'root path of iTunes music library')
    parser.add_argument('--rhythmbox-playlist-path', default = DEFAULT_RHYTHMBOX_PLAYLIST_PATH, help = 'path to Rhythmbox playlist XML')
    parser.add_argument('--rhythmbox-music-root', default = DEFAULT_RHYTHMBOX_MUSIC_ROOT, help = 'root path of Rhythmbox music library')
    args = parser.parse_args()
    itunes_music_root = expanduser(args.itunes_music_root)
    itunes_music_root_escaped = quote(itunes_music_root)
    rhythmbox_music_root = args.rhythmbox_music_root  # don't resolve this path locally
    rhythmbox_music_root_escaped = quote(rhythmbox_music_root)
    lib = get_itunes_library(args.itunes_lib_path)
    root = etree.Element('rhythmdb-playlists')
    tracks = lib['Tracks']
    for playlist in lib['Playlists']:
        playlist_name = playlist['Name']
        if ('Folder' in playlist) or (playlist_name in IGNORED_PLAYLISTS) or (not bool(playlist.get('Playlist Items'))):
            continue
        attrs = {'name' : playlist['Name'], 'show-browser' : 'true', 'browser-position' : '231', 'search-type' : 'search-match', 'type' : 'static'}
        playlist_elt = etree.SubElement(root, 'playlist', attrs)
        for item in playlist['Playlist Items']:
            track = tracks[str(item['Track ID'])]
            location = track.get('Location')
            if (location is None):
                warn_invalid_track(track)
            else:
                location_element = etree.SubElement(playlist_elt, 'location')
                location_element.text = location.replace(itunes_music_root_escaped, rhythmbox_music_root_escaped).replace('localhost/', '')
    logging.info(f'Writing playlist data to {args.rhythmbox_playlist_path}')
    write_xml_to_file(root, args.rhythmbox_playlist_path, add_standalone = False)


if __name__ == '__main__':
    main()