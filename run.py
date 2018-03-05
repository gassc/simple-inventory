from project.app import app

if __name__ == '__main__':
    # Start app
    app.run(
        debug=app.config['DEBUG'],
        host=app.config.get("HOST", "localhost"),
        port=app.config.get("PORT", 8700)
    )
