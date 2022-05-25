### qvalve - Query Valve Main and Game Servers

#### Usage
    qvalve [--max-threads NUM] [--debug] [--show-players] [--show-keywords]
           [--show-tags] [--report-keywords] [--max-servers NUM]
           [--regions NUM [NUM ...]] [--appid NUM] [--empty NUM]
           [--full NUM] [--noplayers NUM] [--map-name NAME]
           [--map-prefix PREFIX] [--min-players NUM] [--no-max-players]
           [--max-ping NUM] [--no-mm-strict-1] [--web-server] [-h] [-v]
           [-V] [--config FILE] [--print-config] [--print-url]
           [ADDR ...]
    
Search Valve's Main server for Game servers.

#### Options
    --max-threads NUM   Run `NUM` threads for game server comms (default:
                        `10`).
    --debug             Pretty-print raw response records (default: `False`).
    --show-players      Print `A2S_PLAYER.names` (default: `False`).
    --show-keywords     Print `A2S_INFO.keywords` (default: `False`).
    --show-tags         Print `A2S_RULES.sv_tags` (default: `False`).
    --report-keywords   Print keywords report (default: `False`).

#### Stage one filters, sent to valve in query to get list of remote game servers
    --max-servers NUM   Get no more than `NUM` servers per region (default:
                        `100`).
    --regions NUM [NUM ...]
                        Get servers for list of regions (default: `[0, 1, 2,
                        3]`).
    --appid NUM         Servers that are running game (default: `440`).
    --empty NUM         Servers that are not empty.
    --full NUM          Servers that are not full.
    --noplayers NUM     Servers that are empty.
    --map-name NAME     Match map `NAME` (exact).
    --map-prefix PREFIX
                        Match map names that start with `PREFIX`.

#### Stage two filters, applied after querying valve
    --min-players NUM   Where number of players is at least NUM.
    --no-max-players    Where number of players is less than its
                        `max_players`.
    --max-ping NUM      Where ping is NUM or less.
    --no-mm-strict-1    Where tf_mm_strict is not 1.

#### Usage 2
    ADDR                Query list of Game server addresses, where ADDR is
                        `IP:PORTNO`.

#### Usage 3
    --web-server        Run web server.

#### General options
    -h, --help          Show this help message and exit.
    -v, --verbose       `-v` for detailed output and `-vv` for more detailed.
    -V, --version       Print version number and exit.
    --config FILE       Use config `FILE` (default: `~/.qvalve.toml`).
    --print-config      Print effective config and exit.
    --print-url         Print project url and exit.
