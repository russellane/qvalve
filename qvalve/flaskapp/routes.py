"""Web app routes."""

import os
import time
from pathlib import Path

import pandas as pd
from flask import Blueprint
from flask import current_app as app
from flask import render_template, request
from loguru import logger

import qvalve.flaskapp.forms
import qvalve.gameserver
import qvalve.mainserver

# -------------------------------------------------------------------------------

bp = Blueprint("bp", __name__, template_folder="templates")

# -------------------------------------------------------------------------------


@bp.route("/", methods=("POST", "GET"))
def index():
    """Home page."""

    form = qvalve.flaskapp.forms.SearchForm()
    data = None
    datalen = 0

    if form.validate_on_submit():
        dataframe = _search(form)
        if dataframe is not None and len(dataframe) > 0:
            data = qvalve.flaskapp.forms.ServerTable(
                dataframe.to_dict("records"), table_id="servers"
            )
            datalen = len(dataframe)

    return render_template("index.html", form=form, data=data, datalen=datalen)


# -------------------------------------------------------------------------------

_MAIN_SERVER = None


def _search(form):

    try:
        global _MAIN_SERVER  # pylint: disable=global-statement
        if not _MAIN_SERVER:
            _MAIN_SERVER = qvalve.mainserver.MainServer(
                max_threads=form.max_threads.data,
                debug=form.debug.data,
            )

        servers = _MAIN_SERVER.search(
            regions=form.regions.data,
            max_servers=form.max_servers.data,
            filters=_get_query_filters(form),
        )
        if servers:
            # objs to dicts
            dataframe = pd.DataFrame([x.__dict__ for x in servers])
            dataframe = _apply_post_query_filters(form, dataframe)
            return dataframe

    except Exception as err:
        raise err
        # logger.error(err)
    return None


# -------------------------------------------------------------------------------


def _get_query_filters(form):

    filters = {"appid": form.appid.data}

    for key, value in [
        ("dedicated", form.dedicated.data),
        ("secure", form.secure.data),
        ("password", form.password.data),
        ("empty", form.empty.data),
        ("full", form.full.data),
        ("noplayers", form.noplayers.data),
    ]:
        if value == "True":
            filters[key] = 1
        elif value == "False":
            filters[key] = 0
        else:
            assert value == "None"

    if form.map_name.data:
        filters["map_name"] = form.map_name.data

    return filters


# -------------------------------------------------------------------------------


def _apply_post_query_filters(form, dataframe):

    if form.map_prefix.data:
        dataframe = dataframe[dataframe.map_name.str.startswith(form.map_prefix.data)]

    if form.min_players.data:
        dataframe = dataframe[dataframe.players > form.min_players.data]

    if form.max_bots.data:
        dataframe = dataframe[dataframe.bots <= form.max_bots.data]

    if form.max_ping.data:
        dataframe = dataframe[dataframe.ping <= form.max_ping.data]

    # sort
    # dataframe.sort_values(['mapname', 'players'], ascending=[True, False], inplace=True)
    dataframe.sort_values(
        ["map_name", "ping", "server_host", "server_port"],
        ascending=[True, True, True, True],
        inplace=True,
    )

    #    # toggle color on map change
    #    c1 = 'bg-default'
    #    c2 = 'bg-dark'
    #    c = c2
    #    lastmap = None
    #    for idx, row in dataframe.iterrows():
    #        if lastmap != row['map']:
    #            c = c1 if c == c2 else c2
    #        lastmap = row['map']
    #        dataframe.at[idx, 'tr_attrs'] = c
    #        # dataframe.at[idx, 'n_imposters'] = int(row['n_imposters'])

    return dataframe


# -------------------------------------------------------------------------------


@bp.route("/connect/<addr>", methods=("POST", "GET"))
def connect(addr):
    """Connect to game server.

    Create a tf2 `exec` script that contains a statement to connect to the
    given server. Run the script manually from tf2's console, or from a
    bound key, e.g. bind F12 "exec user/qvalve-connect.cfg"

    Args:
        addr: address of game server.

    """

    tf2_home = Path.home() / "tf2"  # create symlink if necessary
    if not tf2_home.is_dir():
        tf2_home = Path(".")
    script_name = Path("user", "qvalve-connect.cfg")
    connect_script = Path(tf2_home, "cfg", script_name)

    tag = "QVALVE "
    with open(connect_script, "w", encoding="utf-8") as file:
        print(
            "\n".join(
                [
                    f'echo {tag}{"-" * 40}',
                    f"echo {tag}{script_name}",
                    f"echo {tag}{time.asctime()}",
                    f'echo {tag}{request.args.get("server_name")}',
                    f'echo {tag}{request.args.get("map_name")}',
                    f"connect {addr}",
                ]
            ),
            file=file,
        )

    logger.success(f"Created {str(connect_script)!r} for {addr!r}")
    if app.config["args"].debug:
        os.system(f"/bin/ls -l {connect_script}; /bin/cat {connect_script}")
    return f"Connecting to {addr}"


# -------------------------------------------------------------------------------


@bp.route("/show-players/<addr>", methods=("POST", "GET"))
def show_players(addr):
    """Show players on server at `addr`."""

    logger.debug(f'server_name={request.args.get("server_name")}')
    logger.debug(f'map_name={request.args.get("map_name")}')
    logger.debug(f"addr={addr!r}")

    server = qvalve.gameserver.GameServer(addr)
    server.query()
    # logger.trace(f'server={server}')
    # for playername in server.playernames:
    # logger.trace(f'playername={playername}')
    # for hacker in server.known_hackers:
    # logger.warning(f'known_hacker={hacker}')

    jdoc = server.to_json()
    logger.debug(jdoc)
    return jdoc


# -------------------------------------------------------------------------------
