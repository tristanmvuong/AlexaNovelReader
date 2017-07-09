import pyrebase


def alexa_handler(event, context):
    config = {
        "apiKey": "AIzaSyDizcVyivpWt5ZfuxFh_HIMKdDe5vq9eiY",
        "authDomain": "novelreader-1e068.firebaseapp.com",
        "databaseURL": "https://novelreader-1e068.firebaseio.com",
        "projectId": "novelreader-1e068",
        "storageBucket": "novelreader-1e068.appspot.com",
        "messagingSenderId": "360897853431"
    }

    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password("testsmtpreceiver@gmail.com", "a123456")
    db = firebase.database()

    novelData = db.child("novels").order_by_child("title").equal_to("").get()
    
    # TODO implement
    return 'Hello from Lambda'
