from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Review, Comment, Like

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey123'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    reviews = Review.query.order_by(Review.date_posted.desc()).all()
    return render_template('home.html', reviews=reviews)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post_review():
    if request.method == 'POST':
        title = request.form['title']
        review_type = request.form['review_type']
        rating = int(request.form['rating'])
        content = request.form['content']
        review = Review(title=title, category=review_type, rating=rating, content=content, user_id=current_user.id)

        db.session.add(review)
        db.session.commit()
        flash('Review posted successfully!')
        return redirect(url_for('home'))
    return render_template('post_review.html')

@app.route('/review/<int:review_id>', methods=['GET', 'POST'])
def review_detail(review_id):
    review = Review.query.get_or_404(review_id)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You must log in to comment.')
            return redirect(url_for('login'))
        text = request.form['text']
        comment = Comment(text=text, user_id=current_user.id, review_id=review_id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!')
        return redirect(url_for('review_detail', review_id=review_id))

    comments = Comment.query.filter_by(review_id=review_id).order_by(Comment.date_posted.desc()).all()
    like_count = review.like_count
    user_liked = current_user.id in review.likers if current_user.is_authenticated else False
    return render_template('review_detail.html', review=review, comments=comments, like_count=like_count, user_liked=user_liked)

@app.route('/like/<int:review_id>', methods=['POST'])
@login_required
def like_review(review_id):
    review = Review.query.get_or_404(review_id)
    like = Like.query.filter_by(user_id=current_user.id, review_id=review_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        liked = False
    else:
        new_like = Like(user_id=current_user.id, review_id=review_id)
        db.session.add(new_like)
        db.session.commit()
        liked = True

    like_count = review.like_count
    return jsonify({'liked': liked, 'like_count': like_count})

@app.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash("You are not authorized to delete this review.", "danger")
        return redirect(url_for('home'))

    db.session.delete(review)
    db.session.commit()
    flash("Review deleted successfully.", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
