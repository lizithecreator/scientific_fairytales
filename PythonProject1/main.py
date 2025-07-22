from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from models import db, User, Story
from forms import StoryForm
from auth import auth
from models import SavedStory


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ ცხრილების შექმნა უსაფრთხოდ
with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def home():
    stories = Story.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', stories=stories)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = StoryForm()
    if form.validate_on_submit():
        new_story = Story(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(new_story)
        db.session.commit()
        flash("ზღაპარი დამატებულია!", "success")
        return redirect(url_for('home'))
    return render_template('add.html', form=form)

@app.route('/read/<int:story_id>')
@login_required
def read_story(story_id):
    story = Story.query.get_or_404(story_id)
    return render_template('read_story.html', story=story)

@app.route('/delete/<int:story_id>', methods=['POST'])
@login_required
def delete_story(story_id):
    story = Story.query.get_or_404(story_id)

    SavedStory.query.filter_by(story_id=story.id).delete()

    db.session.delete(story)
    db.session.commit()
    flash('ზღაპარი წაიშალა წარმატებით.', 'success')
    return redirect(url_for('home'))




@app.route('/save/<int:story_id>')
@login_required
def save(story_id):
    story = Story.query.get_or_404(story_id)
    if story in current_user.saved_stories:
        current_user.saved_stories.remove(story)
    else:
        current_user.saved_stories.append(story)
    db.session.commit()
    return redirect(request.referrer or url_for('home'))


@app.route('/others')
@login_required
def others():
    other_stories = Story.query.filter(Story.user_id != current_user.id).all()
    return render_template('others.html', stories=other_stories)



@app.route('/saved')
@login_required
def saved_stories():
    saved = SavedStory.query.filter_by(user_id=current_user.id).all()
    saved_ids = [s.story_id for s in saved]
    stories = Story.query.filter(Story.id.in_(saved_ids)).all()
    return render_template('saved_stories.html', stories=stories)


@app.route('/view/<int:story_id>')
@login_required
def view(story_id):
    story = Story.query.get_or_404(story_id)
    return render_template('view_story.html', story=story)

@app.route('/edit/<int:story_id>', methods=['GET', 'POST'])
@login_required
def edit(story_id):
    story = Story.query.get_or_404(story_id)
    if story.author != current_user:
        abort(403)
    if request.method == 'POST':
        story.title = request.form['title']
        story.content = request.form['content']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit_story.html', story=story)


@app.route('/save/<int:story_id>', methods=['POST'])
@login_required
def save_story(story_id):
    story = Story.query.get_or_404(story_id)
    existing = SavedStory.query.filter_by(user_id=current_user.id, story_id=story.id).first()

    if existing:
        db.session.delete(existing)
    else:
        new_save = SavedStory(user_id=current_user.id, story_id=story.id)
        db.session.add(new_save)

    db.session.commit()
    return redirect(request.referrer or url_for('home'))

@app.route('/story/<int:story_id>')
@login_required
def view_story(story_id):
    story = Story.query.get_or_404(story_id)
    return render_template('view_story.html', story=story)



@app.route('/edit_story/<int:story_id>', methods=['GET', 'POST'])
@login_required
def edit_story(story_id):
    story = Story.query.get_or_404(story_id)
    if story.author != current_user:
        flash("თქვენ არ შეგიძლიათ ამ ზღაპრის რედაქტირება.")
        return redirect(url_for('home'))

    form = StoryForm(obj=story)
    if form.validate_on_submit():
        story.title = form.title.data
        story.content = form.content.data
        db.session.commit()
        flash("ზღაპარი განახლდა წარმატებით!")
        return redirect(url_for('view_story', story_id=story.id))

    return render_template('edit_story.html', form=form, story=story)


if __name__ == '__main__':
    app.run(debug=True)