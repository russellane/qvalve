"""Flask Web Application."""

# -------------------------------------------------------------------------------

from flask import Flask
from loguru import logger

# -------------------------------------------------------------------------------


def run_web_server(args):
    """Create and run Flask Web Application."""

    app = _create_app(
        {
            "BOOTSTRAP_BOOTSWATCH_THEME": "solar",
            "SECRET_KEY": "qvalve",  # secrets.token_urlsafe(16)
            "SEND_FILE_MAX_AGE_DEFAULT": 0,  # DEV MODE ONLY
            "args": args,
        }
    )

    try:
        app.run(host="0.0.0.0")
    except Exception as err:
        logger.critical(f"flask app failed {err}")


# -------------------------------------------------------------------------------


def _create_app(config=None):
    """Create and return Flask Web Application."""

    app = Flask(config.get("name", __name__) if config else __name__)

    if isinstance(config, dict):
        app.config.update(config)

    with app.app_context():
        # PLC0415: Flask app factory pattern requires deferred imports inside app context.
        from flask_babel import Babel  # noqa: PLC0415

        _ = Babel(app)
        # PLC0415: Flask app factory pattern requires deferred imports inside app context.
        from flask_bootstrap import Bootstrap  # noqa: PLC0415

        _ = Bootstrap(app)

        # PLC0415: Flask app factory pattern requires deferred imports inside app context.
        import qvalve.flaskapp.routes  # noqa: PLC0415

        app.register_blueprint(qvalve.flaskapp.routes.bp)
        return app


# -------------------------------------------------------------------------------
