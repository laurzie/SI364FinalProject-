###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
import requests
import json
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,SubmitField,ValidationError,FileField, PasswordField, BooleanField, SelectMultipleField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length, Email, Regexp, EqualTo# Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
# current_user can be used anywhere in the app after login to access the currently logged in user
from werkzeug.security import generate_password_hash, check_password_hash
#protection against db compromises
# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

## App setup code
app = Flask(__name__)
app.debug = True
## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string for si364final'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/laurzieFinal"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)

# App addition setups
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand)

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong' # if generated identifier doesn't match the current user's session, they will be forced to log in again to generate a new identifier
login_manager.login_view = 'login' # display login template when user needs to log in
login_manager.init_app(app) # set up login manager

##################
##### MODELS #####
##################
user_queens = db.Table('user_queens', db.Column('collection_id', db.Integer, db.ForeignKey('queen_collections.id')), db.Column('queen_id', db.Integer, db.ForeignKey('queens.queen_id')))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    collection_of_queens = db.relationship('PersonalQueenCollection',backref = "User")

    # don't let this be readable in case someone gets access to your app
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # never store plain-text passwords
    # when we create a new user, we pass password back, and the below code modifies it from plain-text and inserts it into the password_hash column
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Queens(db.Model):
    __tablename__ = "queens"
    queen_id = db.Column(db.Integer,primary_key=True, autoincrement= False)
    queen_name = db.Column(db.String(60))
    season_winner= db.Column(db.String(5))
    congeniality= db.Column(db.String(5))
    quote = db.Column(db.String(360))
    challenges = db.relationship('Challenges',backref='Queens')

    def __repr__(self):
        return "Queen Name: {}, ID: {}, Quote: {}".format(self.queen_name, self.queen_id, self.quote)

class Challenges(db.Model):
    __tablename__ = "challenges_won"
    challenge_id = db.Column(db.Integer,primary_key=True,autoincrement= False)
    episode_id = db.Column(db.Integer)
    type = db.Column(db.String(60))
    description = db.Column(db.String(180))
    queen_id = db.Column(db.Integer,db.ForeignKey("queens.queen_id"))

    def __repr__(self):
        return "Challenges ID: {}, Episode_id: {}, Description: {}  )".format(self.challenge_id, self.episode_id, self.description)

class Episodes(db.Model):
    __tablename__ = "episodes"
    id = db.Column(db.Integer,primary_key=True)
    episode_number = db.Column(db.String(2))
    title = db.Column(db.String(180))
    season_id = db.Column(db.Integer,db.ForeignKey("seasons.season_id"))

    def __repr__(self):
        return "Episode Number: {}, Title: {}".format(self.episode_number, self.title)

class Seasons(db.Model):
    __tablename__ = "seasons"
    season_id = db.Column(db.Integer,primary_key=True, autoincrement= False)
    season_number = db.Column(db.Integer)
    winner_id = db.Column(db.Integer)
    episodes = db.relationship('Episodes',backref='Seasons')

    def __repr__(self):
        return " Season: {}, winner_id: {})".format(self.season_number, self.winner_id)

class PersonalQueenCollection(db.Model):
    __tablename__ = 'queen_collections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    # This model should have a one-to-many relationship with the User model (one user, many personal collections of gifs with different names -- say, "Happy Gif Collection" or "Sad Gif Collection")
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    # This model should also have a many to many relationship with the Gif model (one gif might be in many personal collections, one personal collection could have many gifs in it).
    queens = db.relationship('Queens', secondary=user_queens, backref=db.backref('queens', lazy='dynamic'), lazy='dynamic')


## DB load function
## Necessary for behind the scenes login manager that comes with flask_login capabilities! Won't run without this.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None
########################
### Helper functions ###
########################

def get_list_of_queens():
    baseurl= 'http://www.nokeynoshade.party/api/queens/all'
    response = requests.get(baseurl)
    text = response.text
    python_obj = json.loads(text)
    list_of_queens = []
    for x in python_obj:
        list_of_queens.append(x["name"])
    return list_of_queens

def get_season_api_info(season_id_number):
    baseurl="http://www.nokeynoshade.party/api/seasons/{}".format(season_id_number)
    response = requests.get(baseurl)
    text = response.text
    python_obj = json.loads(text)
    return python_obj

def get_or_create_season(form_number, season_id_number):
    season = Seasons.query.filter_by(season_number=form_number).first()
    if season:
        flash("Season already entered that season")
    if not season:
        python_obj = get_season_api_info(season_id_number)
        season_number_api = python_obj["seasonNumber"]
        winner_id_api= python_obj["winnerId"]
        season = Seasons(season_id = season_id_number, season_number=season_number_api,winner_id = winner_id_api)
        db.session.add(season)
        db.session.commit()
        get_or_create_episode(season_id_number)
    return season

def get_or_create_episode(season_id_number):
    baseurl = "http://www.nokeynoshade.party/api/seasons/{}/episodes".format(season_id_number)
    response = requests.get(baseurl)
    text = response.text
    python_obj = json.loads(text)
    print("***************\n\n\n")
    print(python_obj)
    for item in python_obj:
        episode_title = item["title"]
        episode_number = item["episodeInSeason"]
        episodes = Episodes(episode_number=episode_number, title = episode_title, season_id = season_id_number)
        db.session.add(episodes)
        db.session.commit()
    return episodes


def get_queen_api_info(queen_name):
    baseurl="http://www.nokeynoshade.party/api/queens?name={}".format(queen_name)
    response = requests.get(baseurl)
    text = response.text
    python_obj = json.loads(text)
    return python_obj

def get_queen_api_info_id(queen_id):
    baseurl="http://www.nokeynoshade.party/api/queens/{}".format(queen_id)
    response = requests.get(baseurl)
    text = response.text
    python_obj = json.loads(text)
    return python_obj

def get_or_create_queen(queen_name):
    print("++++++++")
    print(queen_name)
    queen = Queens.query.filter_by(queen_name = queen_name).first()
    print("\nSTARTING get_or_create_queen\n\n")
    if not queen:
        python_obj = get_queen_api_info(queen_name)
        queen_id_api = python_obj[0]["id"]
        queen_name_api = python_obj[0]["name"]
        winner_api = python_obj[0]["winner"]
        congeniality_api = python_obj[0]["missCongeniality"]
        quote_api = python_obj[0]["quote"]
        queen = Queens(queen_id = queen_id_api, queen_name = queen_name_api, season_winner= winner_api, congeniality = congeniality_api, quote = quote_api  )
        db.session.add(queen)
        db.session.commit()
        print("\nDONE WITH get_or_create_queen\n\n")
    return queen

def get_or_create_collection(name, current_user, queen_list=[]):
    """Always returns a PersonalQueenCollection instance"""
    collection = PersonalQueenCollection.query.filter_by(name=name, user_id=current_user.id).first()
    if not collection:
        collection = PersonalQueenCollection(name=name, user_id=current_user.id)
        for x in queen_list:
            queen = get_or_create_queen(get_queen_api_info_id(x)["name"])
            collection.queens.append(queen)
        db.session.add(collection)
        db.session.commit()
    return collection
###################
###### FORMS ######
###################

class RegistrationForm(FlaskForm):
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User ')

    #Additional checking methods for the form
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

class LoginForm(FlaskForm):
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class SeasonForm(FlaskForm):
    season_number = IntegerField("Please enter the name of the Season(1-10) you want more information on:", validators=[Required()])
    submit = SubmitField()

    def validate_season_name(self, field):
        check_season = field.data.strip()
        list_of_seasons = [0,1,2,3,4,5,6,7,8,9,10]
        errors = None
        if check_season not in list_of_seasons:
            error = "The season number you entered is not valid. Please enter a valid season number"
            raise ValidationError(error)

class QueenForm(FlaskForm):
    queen_name = StringField("Please enter the name of a Drag Queen:", validators=[Required(), Length(1,280)])
    submit = SubmitField()

    def validate_queen_name(self, field):
        check_name = field.data.strip()
        errors = None
        list_of_queens = get_list_of_queens()
        if check_name not in list_of_queens:
            error = "The Drag Queen name you entered is not valid. Please enter a valid name"
            raise ValidationError(error)

class CollectionCreateForm(FlaskForm):
    collection_name = StringField('Collection Name',validators=[Required()])
    queen_picks = SelectMultipleField('Queens to include', coerce=int)
    submit = SubmitField("Create Collection")

    def validate_collection_name(self, field):
        check_collection_name = field.data.strip()
        errors = None
        if "rupaul" in check_collection_name:
            error = "RuPaul is problematic. Please title your collection something else"
            raise ValidationError(error)
        elif "RuPaul" in check_collection_name:
            error = "RuPaul is problematic. Please title your collection something else"
            raise ValidationError(error)

class UpdateButtonForm(FlaskForm):
    submit = SubmitField('Update')

class UpdateInfoForm(FlaskForm):
    new_collection_name = StringField("What is the new collection name?", validators=[Required()])
    submit = SubmitField('Update')

class DeleteButtonForm(FlaskForm):
    submit = SubmitField('Delete')

class EpisodeInput(FlaskForm):
    episode_number = IntegerField("Please enter the number of an episode you want the title on:", validators=[Required()])
    submit = SubmitField()

#######################
###### VIEW FXNS ######
#######################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
            #most of the time url_for(('index'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))



@app.route('/seasons', methods=['GET', 'POST'])
def seasons():
    form = SeasonForm()
    print("\nSTARTING SEASONS\n")
    if form.validate_on_submit():
        form_number= form.season_number.data
        if form_number <= 4:
            season_id_number = form_number
        elif form_number >= 5 and form_number < 9:
            season_id_number = form_number + 1
        elif form_number >= 9 and form_number < 13:
            season_id_number = form_number + 2
        get_or_create_season(form_number = form_number, season_id_number = season_id_number)
        print("\nENDING SEASONS\n")
        return redirect(url_for('get_all_episodes', season_number = form_number))

    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('seasons.html', form=form)

@app.route('/<season_number>')
def get_all_episodes(season_number):
    form_number = int(season_number)
    if form_number <= 4:
        season_id_number = form_number
    elif form_number >= 5 and form_number < 9:
        season_id_number = form_number + 1
    elif form_number >= 9 and form_number < 13:
        season_id_number = form_number + 2
    episodes= Episodes.query.filter_by(season_id = season_id_number)
    return render_template('episodes_by_season.html', episodes = episodes, season_number = form_number)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = QueenForm()
    if form.validate_on_submit():
        queen_name= form.queen_name.data.strip()
        get_or_create_queen(queen_name = queen_name)
        return redirect(url_for('get_queen_info', queen_name = queen_name))

    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html', form=form)

@app.route('/index/<queen_name>')
def get_queen_info(queen_name):
    print("+++++++")
    print("\nHello\n")
    queen= Queens.query.filter_by(queen_name= queen_name).first()
    return render_template('view_queen.html', name = queen.queen_name, quote = queen.quote, winner = queen.season_winner, congeniality = queen.congeniality)

@app.route('/all_queens')
def all_queens():
    queen= Queens.query.all()
    return render_template('all_queens.html', queens = queen)

@app.route('/episodes')
def episode_number():
    return """<form action="http://localhost:5000/title" method='GET'>
    <h1> Get Episode Title </h1>
    Enter in a Episode Number <input type="integer" name="number">
    <input type="submit" value="Submit">
    </form>
    """

@app.route('/title',methods=["GET"])
def get_title():
    if request.method == "GET":
        number = request.args.get('number','')
        print("+++++")
        print(number)
        new_number = int(number) + 7
        baseurl="http://www.nokeynoshade.party/api/episodes/{}".format(new_number)
        response = requests.get(baseurl)
        text = response.text
        python_obj = json.loads(text)
        title = python_obj["title"]
        return "There title of episode {} is {}".format(number, title)
        # Challenge: how would you change this to say "occurrence" in the case there's only 1 'e'?
    return "Nothing was submitted yet... <a href='http://localhost:5000/episodes'>Go submit something</a>"



@app.route('/create_collection',methods=["GET","POST"])
@login_required
def create_collection():
    form = CollectionCreateForm()
    queens = Queens.query.all()
    choices = [(queen.queen_id,queen.queen_name) for queen in queens]
    form.queen_picks.choices = choices
    print(choices)

    if form.validate_on_submit():
        queen_list = [x for x in form.queen_picks.data]

        new_collection = get_or_create_collection(form.collection_name.data, current_user, queen_list)
        return redirect(url_for('collections'))
    return render_template('create_collection.html', form=form)

@app.route('/collections',methods=["GET","POST"])
@login_required
def collections():
    form = UpdateButtonForm()
    formdelete = DeleteButtonForm()
    return render_template('collections.html', form= form, formdelete = formdelete, collections=current_user.collection_of_queens)

@app.route('/collection/<id_num>')
def single_collection(id_num):
    id_num = int(id_num)
    collection = PersonalQueenCollection.query.filter_by(id=id_num).first()
    queen= collection.queens.all()
    return render_template('collection.html',collection=collection, queens=queen)



@app.route('/update/<name>',methods=["GET","POST"])
def update(name):
    form = UpdateInfoForm()
    if form.validate_on_submit():
        print("++++++")
        print(name)
        new_collection_name = form.new_collection_name.data
        l = PersonalQueenCollection.query.filter_by(name=name).first()
        l.name = new_collection_name
        db.session.commit()
        flash("Updated the name of collection " + name)
        return redirect(url_for("collections"))
    return render_template('update_collection_name.html', name = name, form = form)

@app.route('/delete/<name>',methods=["GET","POST"])
def delete(name):
    selected_l = PersonalQueenCollection.query.filter_by(name=name).first()
    db.session.delete(selected_l)
    db.session.commit()
    flash("Deleted Collection {}".format(name))
    return redirect(url_for('collections'))


if __name__ == '__main__':
    db.create_all()
    app.run(use_reloader=True,debug=True)
