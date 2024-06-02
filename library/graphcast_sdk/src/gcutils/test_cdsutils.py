from __future__ import annotations

import os

from graphcast_sdk.src.gcutils.cdsutils import save_cds_file


def test_saves_correctly():
    filename = "tmp.cruft"
    save_cds_file("key", "url", filename)
    with open(filename) as f:
        content = f.read()

    assert content == "key: key\nurl: url\n"
    os.remove(filename)
