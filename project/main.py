from flask import Flask,render_template
from flask import Blueprint
from flask_login import login_required, current_user
from . import db
import os
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
    return render_template('profile.html', name=current_user.name)

@main.route('/choose-self-care')
@login_required
def chooseSelfCare():
    inspoCards = os.listdir(os.path.join(os.getcwd(), 'project/static/inspoCards/'))
    print(inspoCards)
    return render_template('chooseSelfCare.html', title="Choose Self Care",inspoCards=inspoCards)

@main.route('/inspiration')
def explo():
    return render_template('inspo.html', title="Explore Self Care")

@main.route('/journal')
def journal():
    return render_template('journal.html', title="Journal")








if __name__ == '__main__':
  app.run(debug =True)
