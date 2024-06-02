The master branch is only for showcasing the code used for the thesis. To Run the app, you would need access network access to the google cloud environment, as well as google secret manager
to get the environmental variables. The master branch consists of two projects, the RAG project and the Evaluation Framework.

If you wish to run the Evaluation Framework web application, please send a request.

It is not certain that the database is running on the cloud, but a MySQL dump file is provided in the root directory of the project. You can import the database into your local MySQL server to your local database configuration.

And to run the app locally it you would have to do the following:

Create  a virtual environment
$ python3 -m .venv venv

Then activate the virtual environment
$ source .venv/Scripts/activate
and install the requirements with the following command
"$ pip install -r requirements.txt"

And configure your own database, which includes you own database url in the environmental variables.
