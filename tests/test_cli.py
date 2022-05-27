import os

import pytest

from qvalve.cli import main

slow = pytest.mark.skipif(not os.environ.get("SLOW"), reason="slow")


def test_version():
    with pytest.raises(SystemExit) as err:
        main(["--version"])
    assert err.value.code == 0


def test_help():
    with pytest.raises(SystemExit) as err:
        main(["--help"])
    assert err.value.code == 0


def test_md_help():
    with pytest.raises(SystemExit) as err:
        main(["--md-help"])
    assert err.value.code == 0


def test_long_help():
    with pytest.raises(SystemExit) as err:
        main(["--long-help"])
    assert err.value.code == 2


def test_bogus_option():
    with pytest.raises(SystemExit) as err:
        main(["--bogus-option"])
    assert err.value.code == 2


def test_print_config():
    with pytest.raises(SystemExit) as err:
        main(["--print-config"])
    assert err.value.code == 0


def test_print_url():
    with pytest.raises(SystemExit) as err:
        main(["--print-url"])
    assert err.value.code == 0


def test_no_args():
    main(["--regions", "1", "-v"])


@slow
def test_map_name():
    main(["--regions", "1", "-vv", "--map-name", "plr_highertower"])


@slow
def test_map_prefix():
    main(["--regions", "1", "-vv", "--map-prefix", "plr_"])


@slow
def test_debug():
    main(["--regions", "1", "-vvv", "--map-name", "pl_upward", "--debug"])


@slow
def test_show_keywords():
    main(["--regions", "1", "-v", "--map-name", "pl_upward", "--show-keywords"])


@slow
def test_show_players():
    main(["--regions", "1", "-v", "--map-name", "pl_upward", "--show-players"])


@slow
def test_show_tags():
    main(["--regions", "1", "-v", "--map-name", "pl_upward", "--show-tags"])


@slow
def test_report_keywords():
    main(["--regions", "1", "-v", "--report-keywords"])


# def test_web():
#    os.environ['FLASK_APP'] = 'qvalve.web'
#    os.environ['FLASK_ENV'] = 'development'
#    run(
#        args=[
#            'python',
#            '-m',
#            'flask',
#            'run',
#            '--no-debugger',
#        ],
#        check=True,
#    )
