from gallery.factory import create_app

app = create_app()
app.run("127.0.0.1", port=5000, debug=True, use_reloader=False)
