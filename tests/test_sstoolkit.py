
from pytest import raises
from sstoolkit.main import SSToolkitTest

def test_sstoolkit():
    # test sstoolkit without any subcommands or arguments
    with SSToolkitTest() as app:
        app.run()
        assert app.exit_code == 0


def test_sstoolkit_debug():
    # test that debug mode is functional
    argv = ['--debug']
    with SSToolkitTest(argv=argv) as app:
        app.run()
        assert app.debug is True


def test_command1():
    # test command1 without arguments
    argv = ['command1']
    with SSToolkitTest(argv=argv) as app:
        with raises(SystemExit, match="[^0]"):
            app.run()
