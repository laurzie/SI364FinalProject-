# SI364FinalProject-
- [X] Ensure that your SI364final.py file has all the setup (app.config values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on http://localhost:5000 (and the other routes you set up). Your main file must be called SI364final.py, but of course you may include other files if you need.

 - [X] A user should be able to load http://localhost:5000 and see the first page they ought to see on the application.

 - [X] Include navigation in base.html with links (using a href tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, like this )

 - [X]Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.

 - [X] Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).

 - [X] Must have data associated with a user and at least 2 routes besides logout that can only be seen by logged-in users.

 - [x] At least 3 model classes besides the User class.

 - [x] At least one one:many relationship that works properly built between 2 models.

 - [x] At least one many:many relationship that works properly built between 2 models.

 - [X] Successfully save data to each table.

 - [X] Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).

 - [X] At least one query of data using an .all() method and send the results of that query to a template.

 - [X] At least one query of data using a .filter_by(... and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).

 - [X] At least one helper function that is not a get_or_create function should be defined and invoked in the application.

 - [X] At least two get_or_create functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).

 - [X] At least one error handler for a 404 error and a corresponding template.

 - [X] Include at least 4 template .html files in addition to the error handling template files.

- [X] At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.

 - [X] At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that does accord with other involved sites' Terms of Service, etc).

 - [X] Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source to the database (in some way).
 At least one WTForm that sends data with a GET request to a new page.

 -[X] t least one WTForm that sends data with a POST request to the same page. (NOT counting the login or registration forms provided for you in class.)

 - [X] At least one WTForm that sends data with a POST request to a new page. (NOT counting the login or registration forms provided for you in class.)

- [X] At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.

 - [X]Include at least one way to update items saved in the database in the application (like in HW5).

 - [X] Include at least one way to delete items saved in the database in the application (also like in HW5).

 - [X] Include at least one use of redirect.

 - [X] Include at least two uses of url_for. (HINT: Likely you'll need to use this several times, really.)

 - [X] Have at least 5 view functions that are not included with the code we have provided. (But you may have more!)
