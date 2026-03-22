from ledmatrix_server.render import Display

def test_display_starts_dirty():
    display = Display()
    assert display.dirty is True
    