from flask import Flask, request, render_template
from wtforms import Form, StringField
app = Flask(__name__)

class MadpyMemberForm(Form):
    screen_name = StringField('screen_name')


@app.route('/', methods=['GET', 'POST'])
def madpy_habits():
    form = MadpyMemberForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('recommendations.html')
    return render_template('home.html', form=form)
