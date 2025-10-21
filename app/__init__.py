#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    return render_template("pages/home.jinja")


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
@app.get("/sites/")
def show_all_things():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, siteName FROM sites ORDER BY siteName ASC"
        params = []
        result = client.execute(sql, params)
        sites = result.rows

        # And show them on the page
        return render_template("pages/sites.jinja", sites=sites)


#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/site/<int:id>")
def show_one_thing(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT id, siteName, highLevel, lastLevel FROM information WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            thing = result.rows[0]
            return render_template("pages/site.jinja", thing=thing)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_thing():
    # Get the data from the form
    siteName  = request.form.get("Name")
    lastLevel = request.form.get("Most Recent Level")
    highLevel = request.form.get("Highest Level")

    # Sanitize the text inputs
    siteName = html.escape(siteName)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO sites (siteName, lastLevel, highLevel) VALUES (?, ?, ?)"
        params = [siteName, lastLevel, highLevel]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Site '{siteName}' added", "success")
        return redirect("/sites")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM sites WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Site deleted", "success")
        return redirect("/sites")
