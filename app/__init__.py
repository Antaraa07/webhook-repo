from flask import Flask, render_template
from .extensions import mongo
from .webhook.routes import webhook

def create_app():
    app = Flask(__name__, template_folder="../templates")


    # MongoDB configuration
    app.config["MONGO_URI"] = "mongodb+srv://reantara164:J8ABR89XKWFBptyj@cluster0.qha4nn5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    app.config["MONGO_TLS"] = True

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    app.register_blueprint(webhook)

    # Root route to serve the frontend
    @app.route("/")
    def index():
        return render_template("index.html")

    return app
