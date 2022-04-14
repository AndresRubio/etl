from flask import Flask

app = Flask(__name__)

model = []


@app.route('/new_model/url')
def new_model():

    model.append("my_new_model")
    return f"loaded from %s".format('url')


@app.route('/')
def predict():
    return 'you are gonna be rich!!'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
