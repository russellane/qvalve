"""Reports.

Functions to print text reports to stdout.
"""
# -------------------------------------------------------------------------------

from collections import defaultdict

from loguru import logger

import qvalve.gameserver
import qvalve.mainserver

# -------------------------------------------------------------------------------


def search_mainserver(args):
    """Search Valve's Main server for Game servers."""

    mainserver = qvalve.mainserver.MainServer(
        max_threads=args.max_threads,
        debug=args.debug,
        rules=args.show_tags,
    )

    filters = _get_filters_stage1(args)

    servers = mainserver.search(
        regions=args.regions, filters=filters, max_servers=args.max_servers
    )
    logger.success(f"mainserver.search returned {len(servers)} servers")

    servers = _filter_stage2(args, servers)
    logger.success(f"_filter_stage2 returned {len(servers)} servers")

    # key = lambda x: (-x['players'], x['mapname'])  # noqa: E731
    # key = lambda x: (x['mapname'], -x['players'])  # noqa: E731

    _print_gameservers(
        args,
        sorted(servers, key=lambda x: (x.map_name, x.ping, x.addr)),
    )

    if args.report_keywords:
        _print_keywords_report(servers)


# -------------------------------------------------------------------------------


def query_gameservers(args):
    """Query list of Game server addresses."""

    for addr in args.addrs:
        server = qvalve.gameserver.GameServer(addr)
        server.query()
        _print_gameservers(args, [server])


# -------------------------------------------------------------------------------


def _get_filters_stage1(args):
    """Sent to valve in query to get list of remote game servers."""

    filters = {}
    # region is added elsewhere
    if args.appid is not None:
        filters["appid"] = args.appid
    # if args.dedicated is not None:
    #    filters['dedicated'] = args.dedicated
    # if args.secure is not None:
    #    filters['secure'] = args.secure
    # if args.password is not None:
    #    filters['password'] = args.password
    if args.empty is not None:
        filters["empty"] = args.empty
    if args.full is not None:
        filters["full"] = args.full
    if args.noplayers is not None:
        filters["noplayers"] = args.noplayers
    if args.map_name is not None:
        filters["map_name"] = args.map_name

    return filters


# -------------------------------------------------------------------------------


def _filter_stage2(args, servers):
    """Applied after querying valve."""

    if args.map_prefix is not None:
        _ = [x for x in servers if x.map_name.startswith(args.map_prefix)]
        count = len(_)
        logger.info(f"removed {len(servers) - count} servers leaving {count}; map_prefix")
        servers = _

    if args.min_players is not None:  # int
        _ = [x for x in servers if x.players >= args.min_players]
        count = len(_)
        logger.info(f"removed {len(servers) - count} servers leaving {count}; min_players")
        servers = _

    if args.no_max_players:  # bool
        _ = [x for x in servers if x.players < x.max_players]
        count = len(_)
        logger.info(f"removed {len(servers) - count} servers leaving {count}; no_max_players")
        servers = _

    if args.no_mm_strict_1:  # bool
        _ = [x for x in servers if x.visibility != 1]
        count = len(_)
        logger.info(f"removed {len(servers) - count} servers leaving {count}; no_mm_strict_1")
        servers = _

    if args.max_ping is not None:  # int
        _ = [x for x in servers if x.ping <= args.max_ping]
        count = len(_)
        logger.info(f"removed {len(servers) - count} servers leaving {count}; max_ping")
        servers = _

    return servers


# -------------------------------------------------------------------------------


def _print_gameservers(args, servers):

    lastmap = None

    for server in [x for x in servers if x.map_name]:

        if lastmap and lastmap != server.map_name:
            print("-" * 150)
        lastmap = server.map_name

        print(
            " ".join(
                [
                    f"r={server.region:1}",
                    f"app_id={server.app_id:3}",
                    f"typ={server.server_type:1}",
                    f"vac={server.vac:1}",
                    f"vis={server.visibility:1}",
                    f"imp={server.n_imposters:2}",
                    f"a={server.addr:21}",
                    f"ping={server.ping:3}",
                    f"p={server.players:2}",
                    f"m={server.max_players:2}",
                    f"b={server.bots:2}",
                    f"{server.map_name:35}",
                    f"{server.server_name!r}",
                ]
            )
        )

        if args.show_keywords:
            print(f"keywords={server.keywords!r}")

        if args.show_tags:
            print(f".sv_tags={server.sv_tags!r}")

        if args.show_tags and args.show_keywords:
            if not server.keywords or not server.sv_tags:
                logger.warning("missing")
            elif server.sv_tags != server.keywords:
                logger.error("mismatch")
            else:
                logger.success("match")

        if args.show_players:
            for name in server.playernames:
                print(" " * 4 + repr(name))

        for player in server.known_hackers:
            print(player)


# -------------------------------------------------------------------------------


def _print_keywords_report(servers):

    nplayers = defaultdict(int)
    nservers = defaultdict(int)

    for server in [x for x in servers if x.keywords]:
        for k in server.keywords:
            nservers[k] += 1
            nplayers[k] += server.players

    # print('Keywords by number of players:')
    # for key, count in sorted(nplayers.items(), key=lambda _: _[1], reverse=True):
    #    print(f'{count:3} {key}')

    # print('Keywords by number of servers:')
    # for key, count in sorted(nservers.items(), key=lambda _: _[1], reverse=True):
    #    print(f'{count:3} {key}')

    count = 30
    print(f"Top {count} nplayers, nservers")
    _a = sorted(nplayers.items(), key=lambda _: _[1], reverse=True)[:count]
    _b = sorted(nservers.items(), key=lambda _: _[1], reverse=True)[:count]
    for _ in zip(_a, _b):
        print(f"{str(_[0]):30} {str(_[1]):30}")


# -------------------------------------------------------------------------------
