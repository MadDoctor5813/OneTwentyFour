# OneTwentyFour
An election model for the upcoming 2018 Ontario general election.

This repository will not work as-is. For the Django site to function, you must setup a local Postgres database and change the settings in settings.py to point to it. You can then perform the standard Django databse setup process.

In addition, you must upload the ridings_2018.json file using `python manage.py uploadridings <path/to/ridingsfile>`.

Polls must be added using the Django admin interface, and `python manage.py pollaverage` must be run to generate the averages.

Live at onetwentyfour.herokuapp.com
