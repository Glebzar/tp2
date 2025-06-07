import tempfile
from pathlib import Path
from src.scripts.update_index import main
from src.const import VARIOUS_ARTISTS_NAME

def test_main():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        folder = base / "folder"
        folder.mkdir()
        file1 = folder / "song [Artist].mp3"
        file1.write_text("audio")
        main(base)
