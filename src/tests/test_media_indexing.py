import pytest
import tempfile
from pathlib import Path
from src.media_indexing.folder_index import (
    get_artist,
    remove_artist,
    remove_counter,
    get_updated_media_paths,
    apply_new_media_paths,
)
import src.const 
src.const.VARIOUS_ARTISTS_NAME = "Various Artists"
def test_get_artist():
    assert get_artist("[artist]") == "artist"
    assert get_artist("") is None
    with pytest.raises(ValueError):
        get_artist("[artist] [artist]")

def test_remove_artist():
    assert remove_artist("song[artist]") == "song"
    

def test_remove_counter():
    assert remove_counter("Album (3)") == "Album"
    assert remove_counter("Track Name (12)") == "Track Name"
    assert remove_counter("No Counter") == "No Counter"

def test_media_and_folder_rename():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Создание файла
        file = tmp_path / "Track [Test Artist].mp3"
        file.write_text("dummy")

        media = Media(file)
        assert media.artist_name == "Test Artist"
        assert media.title == "Track"
        media.rename_update()
        assert media.path.name == "Track [Test Artist].mp3"

        # Создание папки
        folder_path = tmp_path / "My Album (5)"
        folder_path.mkdir()

        # Добавим внутрь файл
        media_file = folder_path / "Song [Artist].mp3"
        media_file.write_text("content")

        folder = Folder(folder_path)
        assert folder.title == "My Album"
        assert folder.get_counter() == 1
        assert folder.get_new_folder_name() == "My Album (1)"
        folder.rename_with_counter()
        assert folder.path.name == "My Album (1)"

def test_get_updated_media_paths_and_apply():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        folder = base / "Folder1"
        folder.mkdir()
        media_file = folder / "Song [Artist A].mp3"
        media_file.write_text("track content")

        mapping = get_updated_media_paths(base)
        assert len(mapping) == 1

        old_path, new_path = list(mapping.items())[0]
        assert new_path == base / "Artist A" / "Song [Artist A].mp3"

        # Применим перенос
        apply_new_media_paths(mapping)

        assert new_path.exists()
        assert not folder.exists()
