from flask import Flask,render_template, current_app ,Blueprint,request
from flask_login import login_required, current_user
from . import db
import os
import datetime
from datetime import timedelta
main = Blueprint('main', __name__)


@main.route("/")
def home():
    return render_template("homePage.html",title= "TAKE5")

@main.route("/mission")
def mission():
    return render_template("mission.html",title= "Our Mission")




@main.route('/profile')
@login_required
def profile():

    selfCareDict={
    'Meditate -:- Take a few minutes to sit quietly, focus on your breath, and clear your mind. You can also follow guided meditation tutorials on YouTube.':'meditation.jpeg',
    'Journal Your Thoughts -:- Write down your thoughts, feelings, or goals. Journaling helps you process emotions and gain clarity.':'journal.jpeg',
    'Practice Deep Breathing -:- Spend a few minutes focusing on slow, deep breaths to calm your mind and reduce stress.':'practice_deep_breathing.jpeg',
    'Do a Quick Workout -:- Engage in a short, energizing workout like a set of squats, push-ups, or a quick yoga session to boost your mood and energy levels.':'workout.jpeg',
    'Unplug from Devices -:- Take a break from screens and social media. Enjoy some time disconnected from digital distractions.':'devices.jpeg',
    'Stretch Your Body -:- Gently stretch your muscles to release tension and improve flexibility, especially if youve been sitting for a while.':'stretch.jpeg',
    'Drink a Cup of Herbal Tea -:- Sip on a soothing cup of herbal tea to relax and hydrate your body.':'tea.jpeg',
    'Take a Mindful Walk -:- Go for a walk and focus on the sights, sounds, and smells around you. Walking mindfully helps you stay present.':'walk.jpeg',
    'Cook a Healthy Meal -:- Prepare a nutritious meal for yourself, savoring the process of cooking and eating mindfully.':'cook.jpeg',
    'Read or Listen to Something Inspirational -:- Dive into a book, podcast, or article that inspires or uplifts you.':'read.jpeg',
    '':''
    }


    data = current_user.selfCaresCompleted
    currentSelfCare= current_user.currentSelfCare
    name=current_user.name
    streakCount = int(data.split("_")[0].split(":")[1])
    mentalCount =int(data.split("_")[1].split(":")[1])
    physicalCount =int(data.split("_")[2].split(":")[1])
    active_self_care = selfCareDict[currentSelfCare]
    print(active_self_care)
    return render_template('profile.html', name=name,title="Profile",active_self_care=active_self_care,mentalCount=mentalCount,physicalCount=physicalCount,streakCount=streakCount)

@main.route("/choose-self-care-get", methods=["GET", "POST"])
@login_required
def chat():
    name = request.form["name"]
    description = request.form["description"]
    current_user.currentSelfCare = name + "-:-"+ description
    db.session.commit()


@main.route('/choose-self-care')
@login_required
def chooseSelfCare():
    #inspoCards = os.listdir(os.path.join(os.getcwd(), 'project/static/inspoCards/'))
    inspoCards = os.listdir(os.path.join(current_app.root_path, 'static/inspoCards/'))

    selfCareDict={
    'meditation.jpeg':'Meditate -:- Take a few minutes to sit quietly, focus on your breath, and clear your mind. You can also follow guided meditation tutorials on YouTube.',
    'journal.jpeg':'Journal Your Thoughts -:- Write down your thoughts, feelings, or goals. Journaling helps you process emotions and gain clarity.',
    'practice_deep_breathing.jpeg':'Practice Deep Breathing -:- Spend a few minutes focusing on slow, deep breaths to calm your mind and reduce stress.',
    'workout.jpeg':'Do a Quick Workout -:- Engage in a short, energizing workout like a set of squats, push-ups, or a quick yoga session to boost your mood and energy levels.',
    'devices.jpeg':'Unplug from Devices -:- Take a break from screens and social media. Enjoy some time disconnected from digital distractions.',
    'stretch.jpeg':'Stretch Your Body -:- Gently stretch your muscles to release tension and improve flexibility, especially if youve been sitting for a while.',
    'tea.jpeg':'Drink a Cup of Herbal Tea -:- Sip on a soothing cup of herbal tea to relax and hydrate your body.',
    'walk.jpeg':'Take a Mindful Walk -:- Go for a walk and focus on the sights, sounds, and smells around you. Walking mindfully helps you stay present.',
    'cook.jpeg':'Cook a Healthy Meal -:- Prepare a nutritious meal for yourself, savoring the process of cooking and eating mindfully.',
    'read.jpeg':'Read or Listen to Something Inspirational -:- Dive into a book, podcast, or article that inspires or uplifts you.',
    }
    print(inspoCards)
    return render_template('chooseSelfCare.html', title="Choose Self Care",inspoCards=inspoCards,selfCareDict=selfCareDict)

@main.route('/inspiration')
def explo():
    return render_template('inspo.html', title="Explore Self Care")

@main.route('/journal')
def journal():
    return render_template('journal.html', title="Journal")








if __name__ == '__main__':
  app.run(debug =True)
