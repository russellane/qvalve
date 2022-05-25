"""Valve Main Server."""
# -------------------------------------------------------------------------------

import queue
import threading

from loguru import logger
from steam import game_servers as gs

import qvalve.gameserver

# -------------------------------------------------------------------------------


class MainServer:
    """Valve Main Server.

    Interface to 1) search Valve's Main Server for list of Remote Game
    Servers, and 2) multi-thread querying of Remote Game Servers for
    current map, number of players, etc.

    See https://github.com/ValvePython/steam, which is an interface to
    https://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol.

    """

    # pylint: disable=too-few-public-methods

    def __init__(self, max_threads=10, debug=False, rules=False):
        """Initialize MainServer."""

        self._max_threads = int(max_threads)
        self._debug = bool(debug)
        self._rules = bool(rules)
        self._workq = None

    # -------------------------------------------------------------------------------
    # query_master(
    #   filter_text='\\nappid\\500',
    #   max_servers=20,
    #   region=<MSRegion.World: 255>,
    #   master=('hl2master.steampowered.com', 27011),
    #   timeout=2)

    def search(self, regions, **kwargs):
        """Query valve's main server.

        For each region in the list of `regions`, query the main server for
        a list of remote game servers that meet criteria in `filters`,
        which may be a string or a dict. Return `list(dict)`.
        """

        if self._workq is None:
            threading.current_thread().name = "main"
            self._workq = queue.Queue()
            for _ in range(self._max_threads):
                threading.Thread(target=self._a2s_worker, daemon=True).start()

        # `query_master` wants `filter_text` as `type(str)`;
        # also accept `filters` as `type(dict)`.

        if (filters := kwargs.get("filters")) is not None and isinstance(filters, dict):
            delim = "\\"
            filters = delim.join([f"{k}{delim}{v}" for k, v in filters.items()])
            kwargs["filter_text"] = filters
            del kwargs["filters"]

        # build and return this list.
        servers = []

        for region in regions:

            if not isinstance(region, gs.MSRegion):
                region = gs.MSRegion(int(region))
            kwargs["region"] = region
            logger.debug(kwargs)

            # Search Valve's Main Server for list of Remote Game Servers
            # with matching criteria.
            #
            # Create a `GameServer` for each item returned, but don't query
            # them from here (main thread); send them through the workq to
            # workers to perform.

            try:
                for addr in gs.query_master(**kwargs):
                    gameserver = qvalve.gameserver.GameServer(addr, region.value)
                    servers.append(gameserver)
                    self._workq.put(gameserver)

            except RuntimeError as err:
                logger.error(f"{err} query_master({kwargs}")

        # wait for all threads to drain the queue
        self._workq.join()

        # return servers we were able to ping
        return [x for x in servers if x.ping is not None]

    # -------------------------------------------------------------------------------

    def _a2s_worker(self):

        while True:
            try:
                gameserver = self._workq.get()
            except queue.Empty:
                return

            try:
                gameserver.query()
            finally:
                self._workq.task_done()


# -------------------------------------------------------------------------------
