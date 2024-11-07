from  flask import Flask,render_template
from config import Config
from Controller.upload_controller import upload_blueprint

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)


@app.route('/')
def home():
    return render_template('upload.html')
# Register Blueprints
app.register_blueprint(upload_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
