def register_routes(app):
    @app.route('/')
    def index():
        return "Hello World!"
