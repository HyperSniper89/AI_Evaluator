Create  a virtual environment
$ python3 -m .venv venv

Then activate the virtual environment
$ source .venv/Scripts/activate
and install the requirements with the following command
"$ pip install -r requirements.txt"

It is not certain that the database is running on the cloud, but a MySQL dump file is provided in the root directory of the project. You can import the database into your local MySQL server to your local database configuration.