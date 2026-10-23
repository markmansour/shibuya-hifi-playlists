import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "uploader", Path(__file__).parent.parent / "src" / "shibuyahifi-uploader.py")
uploader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uploader)


def album(name, *artists):
    return {'id': name, 'name': name, 'artists': [{'name': a} for a in artists]}


HADESTOWN_CAST = album('Hadestown (Original Broadway Cast Recording)',
                       'Original Broadway Cast of Hadestown', 'Anaïs Mitchell')


def test_title_split_into_artist_and_subtitle():
    candidates = [album('Hadestown', 'Anaïs Mitchell'), HADESTOWN_CAST,
                  album('Hadestown: Live From London', 'Anaïs Mitchell')]
    result = uploader.verify_candidates(candidates, 'Hadestown', 'Original Broadway Cast Recording')
    assert result == [HADESTOWN_CAST]


def test_subtitle_must_match():
    result = uploader.verify_candidates([HADESTOWN_CAST], 'Hadestown', 'Live From London')
    assert result == []
