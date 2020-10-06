import logging
from lxml import etree
from os.path import expanduser
import plistlib
from typing import Any, Dict


logging.basicConfig(level = logging.INFO)

DEFAULT_ITUNES_LIB_PATH = '~/Music/iTunes/iTunes Music Library.xml'
DEFAULT_ITUNES_MUSIC_ROOT = '~/Music/iTunes/iTunes Media/Music'
DEFAULT_RHYTHMBOX_MUSIC_ROOT = '~/Music'
DEFAULT_RHYTHMBOX_ROOT = '~/.local/share/rhythmbox'
DEFAULT_RHYTHMBOX_LIB_PATH = DEFAULT_RHYTHMBOX_ROOT + '/rhythmbox.xml'
DEFAULT_RHYTHMBOX_PLAYLIST_PATH = DEFAULT_RHYTHMBOX_ROOT + '/playlists.xml'


def get_itunes_library(itunes_lib_path: str) -> Dict[str, Any]:
    itunes_lib_path = expanduser(itunes_lib_path)
    with open(itunes_lib_path, 'rb') as f:
        return plistlib.load(f)

def warn_invalid_track(track: Dict[str, Any]) -> None:
    track_name = track['Name']
    artist = track['Artist']
    logging.warning(f'Cannot locate the track [{artist} - {track_name}] (may be a remote file)')

def write_xml_to_file(root: etree._Element, target_path: str, add_standalone: bool = False):
    xml_string = etree.tostring(root, pretty_print = True, xml_declaration = False)
    if add_standalone:
        xml_declaration = '<?xml version="1.0" standalone="yes"?>\n'
    else:
        xml_declaration = '<?xml version="1.0"?>\n'
    final_string = xml_declaration + xml_string.decode('utf-8')
    with open(target_path, 'w') as f:
        print(final_string, file = f)