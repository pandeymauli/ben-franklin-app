from flask import Flask, render_template, redirect, url_for, flash, session, make_response
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, StringField, SubmitField
from wtforms.validators import Required
from flask import request
import requests
import json
import datetime
from datetime import date
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))    # Path to base directory i.e. directory where this app lives
app.config['SECRET_KEY'] = 'woir94823wfnslkfjeout9890284qlwkfmsklmvklmqaee3dwm'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://localhost/bfdb'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['HEROKU_ON'] = os.environ.get('HEROKU')

manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db',MigrateCommand)

def make_shell_context():
    return dict(app=app, db=db, Habit=Habit, DailyCount=DailyCount)

manager.add_command("shell", Shell(make_context=make_shell_context))

### Constants we need for this app
MAX_HABITS = 13
DAYS_IN_A_WEEK = 7
NAME_OF_WEEKDAYS = ['S','M','T','W','T','F','S']
FULLNAME_OF_WEEKDAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
todaysHabitCount = 0
START_DATE = date(2017, 12, 25)
todays_Date = date.today()

class Habit(db.Model):
    __tablename__ = 'habits'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return "Habit {}, description provided {}".format(self.name, self.description)


class DailyCount(db.Model):
    __tablename__ = 'dailycounts'
    date = db.Column(db.DateTime, primary_key=True)
    count = db.Column(db.Integer)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'))


class HabitsForm(FlaskForm):
    def getDefaultValues(i):
        defaultName = ''
        defaultDesc = ''
        # if(Habit.query.filter_by(id=i).first()):
        #     defaultName = Habit.query.filter_by(id=i).first().name
        #     defaultDesc = Habit.query.filter_by(id=i).first().description
        try:
            h = Habit.query.filter_by(id=i).first()
            defaultName = h.name
            defaultDesc = h.description
            print(defaultName, defaultDesc)
        except:
            print('Error occurred!')
        return defaultName, defaultDesc

    i = 1
    h1 = StringField('Habit '+str(i), validators = [Required()], default = getDefaultValues(i)[0])
    h1_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h2 = StringField('Habit '+str(i), validators = [Required()], default = getDefaultValues(i)[0])
    h2_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h3 = StringField('Habit '+str(i), validators = [Required()], default = getDefaultValues(i)[0])
    h3_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h4 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h4_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h5 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h5_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h6 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h6_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h7 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h7_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h8 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h8_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h9 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h9_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h10 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h10_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h11 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h11_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h12 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h12_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    i = i+1
    h13 = StringField('Habit '+str(i), default = getDefaultValues(i)[0])
    h13_desc = TextAreaField('How do you define this habit?', default = getDefaultValues(i)[1])
    submit = SubmitField('DONE')


def habitOfTheWeek(startDate, todaysDate):
    currentWeekNumber = (todaysDate - startDate).days//DAYS_IN_A_WEEK + 1
    list_of_habits = [(h.id, h.name) for h in Habit.query.all()]
    num_of_habits = len(list_of_habits)
    currentWeekHabit = list_of_habits[(currentWeekNumber-1)%num_of_habits]
    return currentWeekHabit


def get_create_or_update_habit(db_session, habit_name, habit_description=''):
        habit = Habit.query.filter_by(name=habit_name).first()
        if(habit):
            habit.description = habit_description
            db.session.commit()
            return habit
        else:
            habit = Habit(name=habit_name, description=habit_description)
            db.session.add(habit)
            db.session.commit()
            return habit


def get_or_create_count_row(db_session, date, habit_id, count=0):
    print("Today's date.... ", date)
    date = datetime.datetime(date.year, date.month, date.day)
    tup = DailyCount.query.filter_by(date=date).first()
    if(tup):
        print("Retrieiving the row for today...")
        if(tup.count > count):
            pass
        else:
            tup.count = count
            db.session.commit()
        return tup
    else:
        print("Creating a row for today...")
        tup = DailyCount(date = date, habit_id = habit_id, count = 0)
        db.session.add(tup)
        db.session.commit()
        return tup


@app.route('/', methods = ['GET','POST'])
def index():
    todaysHabitDetails = habitOfTheWeek(START_DATE, todays_Date)
    habitId = todaysHabitDetails[0]
    habitName = todaysHabitDetails[1]
    tup = get_or_create_count_row(db.session, todays_Date, habitId)
    todaysHabitCount = tup.count
    if request.method == 'POST':
        todaysHabitCount += 1
        tup = get_or_create_count_row(db.session, date = todays_Date, habit_id = habitId, count = todaysHabitCount)
        todaysHabitCount = tup.count
    dayIndex = todays_Date.weekday()
    currentWeekday = ''
    if dayIndex == 6:
        currentWeekday = FULLNAME_OF_WEEKDAYS[-1]
    else:
        currentWeekday = FULLNAME_OF_WEEKDAYS[dayIndex+1]
    return render_template('index.html', count = todaysHabitCount, todaysHabit = habitName, week = FULLNAME_OF_WEEKDAYS, active_day = currentWeekday)

# Serve a form to enter 13 habits
# At least 3 habits are required
@app.route('/enter-habits', methods = ['GET', 'POST'])
def view_and_enter_habits():
    form = HabitsForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        habitsData = form.data
        for i in range(MAX_HABITS):
            habitName_Key = 'h'+str(i+1)
            habitDesc_Key = 'h'+str(i+1)+'_desc'
            if habitsData[habitName_Key]:
                print(get_create_or_update_habit(db.session, habitsData[habitName_Key],habitsData[habitDesc_Key]))
        return redirect(url_for('view_habits'))
    return render_template('habits.html',form=form)


@app.route('/current-habits')
def view_habits():
    habitsEntered = Habit.query.all()
    habitsList = []
    for h in habitsEntered:
        habitName, habitDesc = h.name, h.description
        habitsList.append((habitName, habitDesc))
    print(habitsList)
    return render_template('view-habits.html', num = len(habitsEntered), habitsList=habitsList)

if __name__=='__main__':
    db.create_all()
    manager.run()
