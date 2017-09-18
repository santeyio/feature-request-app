# What is this?

This is a solution to a programming challenge. You can find a live example of the code here http://featurerequests.calebhayashida.com/feature-request

It's an oversimplified internal tool for a web design company to enter in 'feature requests' that their clients make.

(Sidenote, if you want to take a look at my buildbot CI setup just shoot me an email and I can give you creds to check it out). 

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

# Note on the deployment_script.sh

You may notice that there is a bash script included in the project -- I'm using buildbot to watch my repo for Continuous Integration and if commits are pushed to master and the tests pass, then this script is triggered by buildbot to install the newest version of the master branch to the [live example](http://featurerequests.calebhayashida.com/feature-request).
