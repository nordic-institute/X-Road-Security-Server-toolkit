__version__ = "0.1.3"


def setup_hook(argv: list):
    """
    A hook to be used in setup.py to enable `python setup.py publish`.
    :param argv: sys.argv
    """
    if len(argv) > 1 and argv[1] in ["version", "publish", "changelog"]:
        from xrdsst import main

        main()
