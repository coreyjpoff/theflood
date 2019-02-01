# theflood
## Status
Under dev

## Setup Instructions
- The Flood requires the following:

  - pyscopg2, flask in your python 2.7 environment
    - install flask: [sudo] pip install Flask
    - install psycopg2: [sudo] pip install psycopg2

  - a database named 'flood' with user 'flood' that has privileges to delete and
  create tables

- To install the app, install floodmodel:
  - Navigate to the top 'theflood' folder
  - Install the datamodel: [sudo] pip install -e ./theflood/floodmodel/
  - Install theflood app: [sudo] pip install -e .

- After creating the database and installing the app, run 'config.py' to create
the schema and perform other setup

- To start the app, run following commands help w/ running the app using flask:

  - export FLASK_APP=theflood

  - export FLASK_RUN_PORT=8000

  - flask run --host=0.0.0.0 (for testing)

The app is now running. You can access it via a browser @ http://localhost:8000/

## Update 1/26/19:

- Refactoring w/ separation of concerns and adding unit tests in order to make code more
readable and maintainable. This also includes restructuring and deleting obsolete files.
Est finish: 1/31

- Making editor pages dynamic w/ Reactjs interfaces and JavaScript. Est finish: 2/1

- Adding google authentication back. Est finish: 2/4

- Adding basic front end optimization and monitoring (relatively sized images,
  usage stat monitoring, audio support for older browsers, etc...). Est finish: 2/8

- Finish testing and publish. Note to self: Have to reconfigure AWS server. Est finish: 2/11
