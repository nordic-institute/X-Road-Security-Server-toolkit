from xrdsst.main import XRDSSTTest


def test_xrdsst():
    # test sstoolkit without any subcommands or arguments
    with XRDSSTTest() as app:
        app.run()
        assert app.exit_code == 0


def test_xrdsst_debug():
    # test that debug mode is functional
    argv = ['--debug']
    with XRDSSTTest(argv=argv) as app:
        app.run()
        assert app.debug is True
