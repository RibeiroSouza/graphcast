import os

from gcutils.cdsutils import save_cds_file


def test_saves_correctly():
    """Test if the save_cds_file function saves the correct content to a file."""
    filename = "tmp.cruft"
    save_cds_file("key", "url", filename)
    with open(filename) as f:
        content = f.read()

    assert content == "key: key\nurl: url\n"
    os.remove(filename)
