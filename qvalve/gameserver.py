"""Remote Game Server."""
# -------------------------------------------------------------------------------

import json
import socket
from pprint import pprint as pp

# from fuzzywuzzy import fuzz
import steam.game_servers
from loguru import logger

# -------------------------------------------------------------------------------


class GameServer:
    """Remote Game Server.

    Interface to query Remote Game Server for current map, number of players, etc.

    See https://github.com/ValvePython/steam, which is an interface to
    https://developer.valvesoftware.com/wiki/Server_queries.
    """

    # pylint: disable=too-many-instance-attributes
    # -------------------------------------------------------------------------------

    _hackerdb = None
    _debug = None
    _rules = None

    @classmethod
    def configure(cls, args, hackerdb):
        """Configure interface."""

        cls._hackerdb = hackerdb
        cls._debug = args.debug
        cls._rules = args.show_tags

    # -------------------------------------------------------------------------------

    def __init__(self, addr, region=None):
        """Initialize new `GameServer`.

        Args:
            addr: yada
            region: yada
        """

        if not self._hackerdb:
            raise RuntimeError("`configure` not called.")

        if isinstance(addr, str):
            host, port = addr.split(":")
            port = int(port)
        elif isinstance(addr, (list, tuple)):  # noqa: SIM106 Handle error-cases first
            host, port = addr
        else:
            raise SyntaxError(f"expecting str or list, not {type(addr)}; addr={addr!r}")

        self.server_host = host
        self.server_port = int(port)
        self.server_addr = (host, port)
        self.addr = f"{host}:{port}"

        #
        self.region = 9 if region is None else region

        # from `steam.game_servers.a2s_info`
        self.app_id = None
        self.server_type = None
        self.vac = None
        self.visibility = None
        self.players = None
        self.max_players = None
        self.bots = None
        self.map_name = None
        self.server_name = None
        self.keywords = []
        # our extensions
        self.ping = None

        # from `steam.game_servers.a2s_player`
        self.a2s_players = []
        # our extensions
        self.playernames = []
        self.known_hackers = []
        self.n_imposters = 0

        # from `steam.game_servers.a2s_rules`
        # <none; sv_tags comes as string; we split and store as list>
        # our extensions
        self.sv_tags = []

    # -------------------------------------------------------------------------------

    def __str__(self):

        string = f"{self.__class__.__name__}({self.addr!r}"
        if self.map_name:
            string += f", {self.map_name!r}"
        if self.server_name:
            string += f", {self.server_name!r}"
        return string + ")"

    # -------------------------------------------------------------------------------

    def to_json(self):
        """Return json repr of self."""

        serializable = {
            key: value for key, value in self.__dict__.items() if key not in ("known_hackers")
        }
        try:
            return json.dumps(serializable)
        except Exception as err:  # pylint: disable=broad-except
            logger.error(err)
            pp(serializable)
            return {}

    #        return json.dumps({
    #            'region': self.region,
    #            'addr': self.addr,
    #            'app_id': self.app_id,
    #            'server_type': self.server_type,
    #            'vac': self.vac,
    #            'visibility': self.visibility,
    #            'n_imposters': self.n_imposters,
    #            'server_host': self.server_host,
    #            'server_port': self.server_port,
    #            'ping': self.ping,
    #            'players': self.players,
    #            'max_players': self.max_players,
    #            'bots': self.bots,
    #            'map_name': self.map_name,
    #            'server_name': self.server_name,
    #            'a2s_players': self.a2s_players,
    #        })

    # -------------------------------------------------------------------------------

    def query(self):
        """Query Game Server."""

        if self._get_a2s_info():
            self._get_a2s_players()
            if self._rules:
                self._get_a2s_rules()

        # logger.trace(f'server={self}')
        # if self._debug:
        #    pp({'server': self})

    # -------------------------------------------------------------------------------

    def _get_a2s_info(self):
        """Get A2S_INFO data."""

        addr = self.server_addr
        try:
            info = steam.game_servers.a2s_info(addr)
        except socket.timeout:
            return False
        except RuntimeError:  # as err:
            # logger.error(f'{err} a2s_info({addr})')
            return False
        except ConnectionRefusedError:  # as err:
            # logger.error(f'{err} a2s_info({addr})')
            return False

        logger.debug(f"a2s_info({addr})")
        if self._debug:
            pp({"info": info})

        #
        self.app_id = info["app_id"]
        self.server_type = info["server_type"]
        self.vac = info["vac"]
        self.visibility = info["visibility"]
        self.players = info["players"]
        self.max_players = info["max_players"]
        self.bots = info["bots"]
        self.map_name = info["map"]
        self.keywords = info["keywords"].split(",")
        self.ping = int(info["_ping"])  # from float

        # cleanup server names
        self.server_name = "".join([x for x in info["name"] if x.isprintable()]).strip()

        #
        return True

    # -------------------------------------------------------------------------------

    def _get_a2s_players(self):
        """Get A2S_PLAYER data."""

        addr = self.server_addr
        try:
            players = steam.game_servers.a2s_players(addr)
        except socket.timeout:
            return False
        except RuntimeError as err:
            logger.error(f"{err} a2s_players({addr})")
            return False

        logger.debug(f"a2s_players({addr})")
        if self._debug:
            pp({"players": players})

        self.a2s_players = sorted(players, key=lambda x: x["name"].upper())

        for player in self.a2s_players:
            if hackers := self._hackerdb.lookup_name(player["name"]):
                hacker = hackers[0]
                if not hacker.is_gamebot:
                    self.known_hackers.append(hacker)
                    logger.warning(f"hacker={hacker!r}")
                player["attributes"] = hacker.attributes_to_str()
            else:
                player["attributes"] = ""

        # legacy
        self.playernames = sorted(
            [x["name"] for x in self.a2s_players if len(x["name"]) > 0], key=lambda x: x.upper()
        )

        #
        return True

    #
    #        # Identify any known players.
    #        for name in names:
    #            if (player := self._hackerdb.lookup_name(name)):
    #                self.known_hackers.append(player)
    #                if self._debug:
    #                    print(f'found name={name} player={player!r}')
    #            elif self._debug:
    #                print(f'notfound name={name}')
    #
    #        # Check for imposters
    #        while len(names) > 0:
    #
    #            # compare the first name in the list to each of the remaining names in the list.
    #            name = names.pop(0)
    #            self.playernames.append(name)
    #
    #            keep = []
    #            for name2 in names:
    #                ratio = fuzz.ratio(name, name2)
    #                if ratio >= 80:
    #                    # looks like an imposter
    #                    logger.warning(f'ratio={ratio} name={name!r} name2={name2!r}')
    #                    self.n_imposters += 1
    #                    # remove name2 from the list.
    #                    # (nothing to do; it's effectively "removed" by not being kept
    #                    # in `keep`.)
    #                else:
    #                    if self._debug:
    #                        logger.trace(f'ratio={ratio} name={name!r} name2={name2!r}')
    #                    keep.append(name2)
    #
    #            # don't re-check/re-count identified imposters
    #            names = keep
    #
    #        #
    #        self.playernames = sorted(self.playernames, key=lambda x: x.upper())
    #
    #        #
    #        return True

    # -------------------------------------------------------------------------------

    def _get_a2s_rules(self):
        """Get A2S_RULES data."""

        addr = self.server_addr
        try:
            rules = steam.game_servers.a2s_rules(addr)
        except socket.timeout:
            return False
        except RuntimeError as err:
            logger.error(f"{err} a2s_rules({addr})")
            return False

        logger.debug(f"a2s_rules({addr})")
        if self._debug:
            pp({"rules": rules})

        #
        self.sv_tags = rules.get("sv_tags", "").split(",")

        #
        return True


# -------------------------------------------------------------------------------
