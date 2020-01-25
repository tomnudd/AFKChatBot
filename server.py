from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/creds/<email>/<password>', methods=['GET', 'POST'])
def credsgiven(email, password):
    print("FUCK")
    return "Logged In"

if __name__ == '__main__':
    app.run()
