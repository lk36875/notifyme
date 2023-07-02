from notify.app import create_app


def run() -> None:
    """
    Run the NotifyMe API.

    This function creates a new Flask application using the `create_app` function from the `notify.app` module.
    """
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
