# What is this?

This is a solution to a programming challenge, specified [here](https://github.com/IntuitiveWebSolutions/EngineeringMidLevel). You can find a live example of the code here http://featurerequests.calebhayashida.com/feature-request

# Installation

Create a new virtualenv and activate it

```
$ virtualenv feature-requests
$ cd feature-requests
$ source bin/activate 
```

Clone this project and install the requirements

```
(feature-requests) $ git clone https://github.com/santeyio/feature-request-app.git
(feature-requests) $ cd feature-request-app
(feature-requests) $ pip install -r requirements.txt
```

# Creating the database

Now you need to create a development database. It will reside in your virtualenv directory, the directory above your flask application directory. Simply open a python interpreter and run the create_db helper.

```
$ python
>>> from featurerequests import create_db
>>> create_db()
```

Now you should have a test.db squlite file in the directory above your application.

# Running the flask app

You can run the app with gunicorn for production, but for running it locally just use flask's development server:

```
(feature-requests) $ export FLASK_APP=featurerequests.py
(feature-requests) $ export FLASK_DEBUG=True
(feature-requests) $ flask run
```

And you should be able to access the site at http://127.0.0.1:5000
