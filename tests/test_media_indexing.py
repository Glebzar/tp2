import pytest
import tempfile
from pathlib import Path
from unittest.mock import call
from unittest.mock import MagicMock, patch
from src.media_indexing.folder_index import (
    get_artist,
    remove_artist,
    remove_counter,
    get_updated_media_paths,
    apply_new_media_paths,
    Media,
    Folder,
    get_folders,
    get_folder_files,
    reindex_folders
)
import src.const 
src.const.VARIOUS_ARTISTS_NAME = "Various Artists"
def test_get_artist():
    assert get_artist("[artist]") == "Artist"
    assert get_artist("") is None
    with pytest.raises(ValueError):
        get_artist("[artist] [artist]")

def test_remove_artist():
    assert remove_artist("song[artist]") == "song"
    assert remove_artist("song") == "song"

def test_init():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        file = tmp_path / "song [artist]"
        file.write_text("data")
        media = Media(file)
        assert media.artist_name == "Artist"
        assert media.title == "song"
        assert media.path == file
        tmp_path = Path(tmpdir)
        file = tmp_path / "song"
        file.write_text("data")
        media = Media(file)
        assert media.artist_name is None
        assert media.title == "song"

def test_rename_update():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        file = tmp_path / "song [artist].mp3"
        file.write_text("audio")
        media = Media(file)
        media.rename_update()
        expected_name = "song [Artist].mp3"
        expected_path = tmp_path / expected_name
        assert media.path == expected_path
        assert expected_path.exists()

def test_remove_counter():
    assert remove_counter("song (3)") == "song"
    assert remove_counter("song") == "song"

def test_init_raises(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")
    with pytest.raises(ValueError):
        Folder(file_path)

@pytest.fixture
def media_folder(tmp_path):
    folder = tmp_path / "test"
    folder.mkdir()
    (folder / "song1.mp3").write_text("a")
    (folder / "song2.mp3").write_text("b")
    return folder

def test_get_media_list(media_folder):
    folder = Folder(media_folder)
    assert len(folder.get_media_list()) == 2

def test_get_counter(media_folder):
    folder = Folder(media_folder)
    assert folder.get_counter() == 2

def test_get_new_folder_name(media_folder):
    folder = Folder(media_folder)
    assert folder.get_new_folder_name() == "test (2)"

def test_rename_with_counter(media_folder):
    folder = Folder(media_folder)
    folder.rename_with_counter()
    assert folder.path.name == "test (2)"
    assert folder.path.exists()

def test_get_folders(tmp_path):
    (tmp_path / "folder1").mkdir()
    (tmp_path / ".folder2").mkdir()
    folders = get_folders(tmp_path)
    folder_names = [f.path.name for f in folders]
    assert set(folder_names) == {"folder1"}

def test_get_folder_files(tmp_path):
    (tmp_path / "file1.mp3").write_text("data")
    (tmp_path / ".file2.mp3").write_text("hidden")
    files = get_folder_files(tmp_path)
    file_names = [f.name for f in files]
    assert "file1.mp3" in file_names
    assert ".file2.mp3" not in file_names



def test_get_updated_media_paths(tmp_path):
    media1 = MagicMock()
    media1.artist_name = "Artist"
    media1.path = tmp_path / "folder1" / "song1.mp3"
    media2 = MagicMock()
    media2.artist_name = None  
    media2.path = tmp_path / "folder2" / "song2.mp3"
    folder1 = MagicMock()
    folder1.get_media_list.return_value = [media1]
    folder2 = MagicMock()
    folder2.get_media_list.return_value = [media2]
    with patch("src.media_indexing.folder_index.get_folders", return_value=[folder1, folder2]), \
         patch("src.media_indexing.folder_index.VARIOUS_ARTISTS_NAME", "Various Artists"):
        mapping = get_updated_media_paths(tmp_path)
        assert mapping[media1.path] == tmp_path / "Artist" / media1.path.name
        assert mapping[media2.path] == tmp_path / "Various Artists" / media2.path.name

def test_apply_new_media_paths(tmp_path):
    file1 = tmp_path / "folder" / "song.mp3"
    folder1 = file1.parent
    file2 = tmp_path / "Artist" / "song.mp3"
    folder1.mkdir()
    file1.write_text("audio")
    mapping = {file1: file2}
    with patch("src.media_indexing.folder_index.get_folder_files", return_value=[]), \
         patch("pathlib.Path.rename") as mock_rename, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("shutil.rmtree") as mock_rmtree:
        apply_new_media_paths(mapping)
        mock_mkdir.assert_called_once_with(exist_ok=True)
        mock_rename.assert_called_once_with(file2)
        mock_rmtree.assert_called_once_with(folder1)

def test_reindex_folders(tmp_path):
    media_mock = MagicMock()
    folder_mock = MagicMock()
    folder_mock.get_media_list.return_value = [media_mock]
    reindex_folders([folder_mock])
    media_mock.rename_update.assert_called_once()
    folder_mock.rename_with_counter.assert_called_once()

