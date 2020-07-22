from flask import Flask

app = Flask(__name__)


@app.route('/compute/v1/input')
def hello_world():
    return 'Hello world'


if __name__ == '__main__':
    app.run(host='0.0.0.0')