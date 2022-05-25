"""Command line interface."""

import sys
from pathlib import Path
from typing import List, Optional

import tf2mon.hacker
from libcli import BaseCLI
from loguru import logger
from steam.game_servers import MSRegion

import qvalve.flaskapp
import qvalve.gameserver
import qvalve.reports


class QvalveCLI(BaseCLI):
    """Command line interface."""

    config = {
        # name of config file.
        "config-file": Path.home().joinpath(".qvalve.toml"),
        # toml [section-name].
        "config-name": "qvalve",
        # application
        "gamebots": Path(__file__).parent.joinpath("data/gamebots.csv"),
        "max-threads": 10,
        "max-servers": 100,
    }

    def init_logging(self, verbose: int) -> None:
        """Set loguru logging level based on `--verbose`."""

        if not self.init_logging_called:
            super().init_logging(verbose)
            _ = ["INFO", "DEBUG", "TRACE"]
            level = _[min(verbose, len(_) - 1)]
            logger.remove()
            logger.add(sys.stderr, level=level)

    def init_parser(self) -> None:
        """Initialize argument parser."""

        self.parser = self.ArgumentParser(
            prog=__package__,
            description="Search Valve's Main server for Game servers.",
        )

    def set_defaults(self):
        """Set defaults."""

        self.parser.set_defaults(
            max_threads=self.config["max-threads"],
            debug=False,
            show_players=False,
            show_keywords=False,
            show_tags=False,
            report_keywords=False,
            # stage1 filters
            max_servers=self.config["max-servers"],
            regions=[
                MSRegion.US_East.value,
                MSRegion.US_West.value,
                MSRegion.South_America.value,
                MSRegion.Europe.value,
                # MSRegion.Asia.value,
                # MSRegion.Australia.value,
                # MSRegion.Middle_East.value,
                # MSRegion.Africa.value,
                # MSRegion.World.value,
            ],
            appid=440,  # Servers that are running game
            # these have no effect in testing, so disabling.
            # dedicated=None,   # Servers running dedicated
            # secure=None,      # Servers using anti-cheat technology
            # password=None,    # Servers that are not password protected
            empty=None,  # Servers that are not empty
            full=None,  # Servers that are not full
            noplayers=None,  # Servers that are empty
            map_name=None,  # exact match; 'plr_pipeline'
            # stage2 filters
            min_players=None,
            no_max_players=None,
            max_ping=None,
            no_mm_strict_1=None,
            map_prefix=None,  # prefix match; 'plr_'
            # usage 2
            addrs=[],
            # usage 3
            web_server=False,
        )

    def add_arguments(self) -> None:
        """Add arguments to parser."""

        # usage 1
        arg = self.parser.add_argument(
            "--max-threads",
            metavar="NUM",
            type=int,
            help="Run `NUM` threads for game server comms.",
        )
        self.add_default_to_help(arg)

        arg = self.parser.add_argument(
            "--debug",
            action="store_true",
            help="Pretty-print raw response records",
        )
        self.add_default_to_help(arg)

        arg = self.parser.add_argument(
            "--show-players",
            action="store_true",
            help="Print `A2S_PLAYER.names`",
        )
        self.add_default_to_help(arg)

        arg = self.parser.add_argument(
            "--show-keywords",
            action="store_true",
            help="Print `A2S_INFO.keywords`",
        )
        self.add_default_to_help(arg)

        arg = self.parser.add_argument(
            "--show-tags",
            action="store_true",
            help="Print `A2S_RULES.sv_tags`",
        )
        self.add_default_to_help(arg)

        arg = self.parser.add_argument(
            "--report-keywords",
            action="store_true",
            help="Print keywords report",
        )
        self.add_default_to_help(arg)

        # -------------------------------------------------------------------------------

        stage1 = self.parser.add_argument_group(
            "Stage one filters, sent to valve in query to get list of remote game servers"
        )
        arg = stage1.add_argument(
            "--max-servers",
            metavar="NUM",
            type=int,
            help="Get no more than `NUM` servers per region",
        )
        self.add_default_to_help(arg)

        arg = stage1.add_argument(
            "--regions",
            metavar="NUM",
            type=int,
            nargs="+",
            help="Get servers for list of regions",
        )
        self.add_default_to_help(arg)

        arg = stage1.add_argument(
            "--appid",
            metavar="NUM",
            type=int,
            help="Servers that are running game",
        )
        self.add_default_to_help(arg)

        # stage1.add_argument('--dedicated', metavar='NUM', type=int,
        #   help='Servers running dedicated')
        # stage1.add_argument('--secure', metavar='NUM', type=int,
        #   help='Servers using anti-cheat technology')
        # stage1.add_argument('--password', metavar='NUM', type=int,
        #   help='Servers that are not password protected')

        arg = stage1.add_argument(
            "--empty",
            metavar="NUM",
            type=int,
            help="Servers that are not empty",
        )

        arg = stage1.add_argument(
            "--full",
            metavar="NUM",
            type=int,
            help="Servers that are not full",
        )

        arg = stage1.add_argument(
            "--noplayers",
            metavar="NUM",
            type=int,
            help="Servers that are empty",
        )

        arg = stage1.add_argument(
            "--map-name",
            metavar="NAME",
            help="Match map `NAME` (exact)",
        )

        # -------------------------------------------------------------------------------

        stage2 = self.parser.add_argument_group(
            "Stage two filters, applied after querying valve",
        )
        stage1.add_argument(
            "--map-prefix",
            metavar="PREFIX",
            help="Match map names that start with `PREFIX`",
        )

        stage2.add_argument(
            "--min-players",
            metavar="NUM",
            type=int,
            help="where number of players is at least NUM",
        )

        stage2.add_argument(
            "--no-max-players",
            action="store_true",
            help="where number of players is less than its `max_players`",
        )

        stage2.add_argument(
            "--max-ping",
            metavar="NUM",
            type=int,
            help="where ping is NUM or less",
        )

        stage2.add_argument(
            "--no-mm-strict-1",
            action="store_true",
            help="where tf_mm_strict is not 1",
        )

        #
        usage2 = self.parser.add_argument_group("Usage 2")
        usage2.add_argument(
            "addrs",
            metavar="ADDR",
            nargs="*",
            help="Query list of Game server addresses, where ADDR is `IP:PORTNO`",
        )

        #
        usage3 = self.parser.add_argument_group("Usage 3")
        usage3.add_argument(
            "--web-server",
            action="store_true",
            help="Run web server",
        )

    def main(self) -> None:
        """Command line interface entry point (method)."""

        hackers = tf2mon.hacker.Hackers()
        hackers.load_gamebots(self.config["gamebots"])
        qvalve.gameserver.GameServer.configure(self.options, hackers)

        if self.options.web_server:
            # usage 3
            qvalve.flaskapp.run_web_server(self.options)

        elif self.options.addrs:
            # usage 2
            qvalve.reports.query_gameservers(self.options)

        else:
            # usage 1
            qvalve.reports.search_mainserver(self.options)


def main(args: Optional[List[str]] = None) -> None:
    """Command line interface entry point (function)."""
    return QvalveCLI(args).main()
