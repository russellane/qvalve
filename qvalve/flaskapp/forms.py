"""Web app forms."""

from flask import current_app as app
from flask_table import Col, Table
from flask_wtf import FlaskForm
from steam import game_servers as gs
from wtforms import (
    BooleanField,
    IntegerField,
    RadioField,
    SelectMultipleField,
    StringField,
    SubmitField,
    validators,
    widgets,
)

# -------------------------------------------------------------------------------


class ServerTable(Table):
    """ServerTable."""

    classes = ["table", "table-sm", "table-condensed", "table-bordered"]

    region = Col("Region")
    app_id = Col("Appid")
    server_type = Col("ST")
    vac = Col("Vac")
    visibility = Col("Vis")
    n_imposters = Col("Imp", column_html_attrs={"class": "text-right"})
    server_host = Col("Host")
    server_port = Col("Port")
    ping = Col("Ping", column_html_attrs={"class": "text-right"})
    players = Col("Players", column_html_attrs={"class": "text-right"})
    max_players = Col("Max", column_html_attrs={"class": "text-right"})
    bots = Col("Bots", column_html_attrs={"class": "text-right"})
    map_name = Col("Map")
    server_name = Col("Name")
    # keywords        = Col('Keywords')

    # -------------------------------------------------------------------------------

    def get_tr_attrs(self, item):
        """Return table row attributes for `item`."""

        classes = "server"
        if (attrs := item.get("tr_attrs")) is not None:
            classes += " " + attrs

        return {
            "class": classes,
            "addr": item["addr"],
        }

    # -------------------------------------------------------------------------------

    def sort_url(self, col_id, reverse=False):
        """W0223.

        Method 'sort_url' is abstract in class 'Table' but is not
        overridden (abstract-method).
        """


# -------------------------------------------------------------------------------
# other available properties
#   '_ping',        # 108.20508003234863
#   '_type',        # 'source'
#   'edf',          # 177
#   'environment',  # 'l'
#   'folder',       # 'tf'
#   'game',         # '\x01  ►  Gun Game  ◄'
#   'game_id',      # 440
#   'keywords',     # 'alltalk,blackwonder,cp,game,gg,gun,gungame,ranks'
#   'port',         # 27075
#   'protocol',     # 17
#   'steam_id',     # 85568392921190943
#   'version',      # '6300758'

# -------------------------------------------------------------------------------


class MultiCheckboxField(SelectMultipleField):
    """MultiCheckboxField."""

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# -------------------------------------------------------------------------------


class RadioBool(RadioField):
    """RadioBool."""

    def __init__(self, label="", validators_=None, **kwargs):
        """Initialize RadioBool."""

        kwargs["choices"] = [("None", "Unspecified"), ("True", "True"), ("False", "False")]
        if not kwargs.get("default"):
            kwargs["default"] = "None"
        kwargs["render_kw"] = {"class": "btn-check"}
        super().__init__(label, validators_, **kwargs)


# -------------------------------------------------------------------------------


class SearchForm(FlaskForm):
    """SearchForm."""

    # search engine
    max_threads = IntegerField(
        "Max Threads",
        [validators.NumberRange(1, 100, "Please enter a number from 1 to 100")],
        default=app.config["args"].max_threads,
        render_kw={"size": 4},
    )
    debug = BooleanField("Debug", default=app.config["args"].debug)

    # stage1 filters
    max_servers = IntegerField(
        "Max Servers", default=app.config["args"].max_servers, render_kw={"size": 4}
    )
    regions = MultiCheckboxField(
        "Regions",
        choices=[(str(x.value), x.name) for x in gs.MSRegion],
        default=[
            str(x.value)
            for x in (
                gs.MSRegion.US_East,
                gs.MSRegion.US_West,
                gs.MSRegion.South_America,
                gs.MSRegion.Europe,
                # gs.MSRegion.Asia.value,
                # gs.MSRegion.Australia.value,
                # gs.MSRegion.Middle_East.value,
                # gs.MSRegion.Africa.value,
                # gs.MSRegion.World.value,
            )
        ],
    )

    appid = IntegerField("AppID", [validators.optional()], default=440, render_kw={"size": 4})
    dedicated = RadioBool("Dedicated")
    secure = RadioBool("Secure")
    password = RadioBool("Password")
    empty = RadioBool("Not Empty", default="True")
    full = RadioBool("Not Full", default="True")
    noplayers = RadioBool("No Players")
    map_name = StringField(
        "Map name", default=app.config["args"].map_name, render_kw={"size": 30}
    )
    map_prefix = StringField(
        "Map prefix", default=app.config["args"].map_prefix, render_kw={"size": 30}
    )

    # stage2 filters go here

    min_players = IntegerField("Min Players", [validators.optional()], render_kw={"size": 4})
    max_bots = IntegerField("Max Bots", [validators.optional()], render_kw={"size": 4})
    max_ping = IntegerField("Max Ping", [validators.optional()], render_kw={"size": 4})

    #
    submit = SubmitField("Search", render_kw={"class": "btn btn-primary btn-lg btn-block"})


# -------------------------------------------------------------------------------
