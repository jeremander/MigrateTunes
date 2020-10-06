#!/usr/bin/env python3
"""Integrates song info into Rhythmbox."""

import argparse
import logging
from lxml import etree
from os.path import expanduser
from typing import Any
from urllib.parse import quote

from .utils import DEFAULT_ITUNES_LIB_PATH, DEFAULT_ITUNES_MUSIC_ROOT, DEFAULT_RHYTHMBOX_LIB_PATH, DEFAULT_RHYTHMBOX_MUSIC_ROOT, get_itunes_library, warn_invalid_track, write_xml_to_file

PREFIX_ITUNES_ON_WINDOWS = 'file://localhost/'
PREFIX_ITUNES_ON_MAC = 'file://'
PREFIX_RHYTHMBOX = 'file://'

ITUNES_TO_RHYTHMBOX_RATINGS = {0: 0, 20: 1, 40: 2, 60: 3, 80: 4, 100: 5, None: None}


def canonical_location_from_itunes(itunes_location: str, itunes_music_root: str) -> str:
    if itunes_location.startswith(PREFIX_ITUNES_ON_WINDOWS):
        return itunes_location.replace(PREFIX_ITUNES_ON_WINDOWS + itunes_music_root, '')
    if itunes_location.startswith(PREFIX_ITUNES_ON_MAC):
        return itunes_location.replace(PREFIX_ITUNES_ON_MAC + itunes_music_root, '')
    logging.warning(f"The iTunes location {itunes_location} doesn't start with a known prefix. It's likely that we can't match it later to a Rhythmbox path.")
    return itunes_location

def canonical_location_from_rhythmbox(rhythmbox_location: str, rhythmbox_music_root: str):
    if rhythmbox_location.startswith(PREFIX_RHYTHMBOX):
        return rhythmbox_location.replace(PREFIX_RHYTHMBOX + rhythmbox_music_root, '')
    logging.warning(f"The rhythmbox location {rhythmbox_location} doesn't start with a known prefix. It's likely that we can't match it later to an iTunes path.")
    return rhythmbox_location

def integrate_value_to_rhythmdb_song(rhythmdb_song: etree._Element, rhythmdb_node_name: str, itunes_value: Any):
    rhythmdb_value_node = rhythmdb_song.find(rhythmdb_node_name)
    if itunes_value is None and rhythmdb_value_node is not None:
        rhythmdb_song.remove(rhythmdb_value_node)
    elif itunes_value is not None and rhythmdb_value_node is None:
        rhythmdb_value_node = etree.SubElement(rhythmdb_song, rhythmdb_node_name)
        rhythmdb_value_node.text = str(itunes_value)
    elif itunes_value is not None and rhythmdb_value_node is not None:
        rhythmdb_value_node.text = str(itunes_value)


def main() -> None:
    parser = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--itunes-lib-path', default = DEFAULT_ITUNES_LIB_PATH, help = 'path to iTunes library XML')
    parser.add_argument('--itunes-music-root', default = DEFAULT_ITUNES_MUSIC_ROOT, help = 'root path of iTunes music library')
    parser.add_argument('--rhythmbox-lib-path', default = DEFAULT_RHYTHMBOX_LIB_PATH, help = 'path to Rhythmbox library XML')
    parser.add_argument('--rhythmbox-music-root', default = DEFAULT_RHYTHMBOX_MUSIC_ROOT, help = 'root path of Rhythmbox music library')
    args = parser.parse_args()
    itunes_music_root = expanduser(args.itunes_music_root)
    itunes_music_root_escaped = quote(itunes_music_root)
    rhythmbox_music_root = args.rhythmbox_music_root  # don't resolve this path locally
    rhythmbox_music_root_escaped = quote(rhythmbox_music_root)
    lib = get_itunes_library(args.itunes_lib_path)
    # gather song statistics
    logging.info('Gathering song stats...')
    song_stats = {}
    for track in lib['Tracks'].values():
        location = track.get('Location')
        if (location is None):
            warn_invalid_track(track)
        else:
            play_count = track.get('Play Count', 0)
            last_played = track.get('Play Date UTC')
            itunes_rating = track.get('Rating')
            rhythmbox_rating = ITUNES_TO_RHYTHMBOX_RATINGS[itunes_rating]
            loc = canonical_location_from_itunes(location, itunes_music_root_escaped)
            song_stats[loc] = {'play-count' : play_count, 'rating' : rhythmbox_rating, 'last-played' : last_played}
    # integrate stats
    logging.info('Integrating song stats...')
    rhythmdb = etree.parse(args.rhythmbox_lib_path)
    root = rhythmdb.getroot()
    songs = root.getchildren()
    songs_changed = 0
    for song in songs:
        location = song.find('location').text
        loc = canonical_location_from_rhythmbox(location, rhythmbox_music_root_escaped)
        if (loc in song_stats):
            songs_changed += 1
            d = song_stats[loc]
            for (key, val) in d.items():
                integrate_value_to_rhythmdb_song(song, key, val)
    if (songs_changed > 0):
        logging.info(f'Updated {songs_changed:,d} entries')
    else:
        logging.info('No songs have been changed (probably because the iTunes and Rhythmbox song paths could not be matched together). Please check your --itunes-music-root and --rhythmbox-music-root paths.')
    logging.info(f'Writing updated song data to {args.rhythmbox_lib_path}')
    write_xml_to_file(root, args.rhythmbox_lib_path, add_standalone = False)

if __name__ == '__main__':
    main()