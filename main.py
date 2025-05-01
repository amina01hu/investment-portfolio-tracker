import finnhub
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import sqlite3
from db.database import create_tables, connect_db
from models import User, Portfolio, Asset
from dotenv import load_dotenv
import os

create_tables()

load_dotenv()
# create flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
api_key = os.getenv("API_KEY")

# Setup client
finnhub_client = finnhub.Client(api_key=api_key)


@app.route('/')
def index():
    return render_template('index.html')

# login template
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get("login")
        if action == "Login":
            email = request.form['email']
            password = request.form['password']
            logged_in_user = User.find_by_credentials(email, password)
            if logged_in_user:
                session['user_profile'] = (logged_in_user.user_id, logged_in_user.fname, logged_in_user.lname, logged_in_user.email) # Save user's ID in session
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))  # Redirect after login
            else:
                flash('Login failed', 'danger')
        
    return render_template('login.html')

# @app.route('/')
# def dashboard():
#     portfolio = Portfolio.query.all()
#     return render_template('dashboard.html', portfolio=portfolio)

@app.route('/add', methods=['POST'])
def add_portfolio():
    if 'user_profile' not in session:
        flash("You must be logged in to add portfolio.", "danger")
        return redirect(url_for('login'))
    user_id = session['user_profile'][0]
    portfolio_name = request.form.get('portfolio_name')
    portfolio_desc = request.form.get('portfolio_desc')
    if portfolio_name and portfolio_desc:
        portfolio = Portfolio(user_id, portfolio_name, portfolio_desc)
        if portfolio.save():
            flash("Portfolio added successfully!", "success")
        else:
            flash("Error saving portfolio.", "danger")
    else:
        flash("Name and Description.", "warning")
    return redirect(url_for('dashboard'))

# protected route for users only
@app.route('/dashboard')
def dashboard():
    if not session['user_profile']:
        flash("Please log in first", "warning")
        return redirect(url_for('login'))
    app.logger.info(f"logged in successfully")
    user_id = session.get('user_profile')[0]
    portfolios = Portfolio.get_by_id(user_id)
    return render_template('dashboard.html', portfolio=portfolios, user_id=user_id)

# sign up form
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        action = request.form.get("new_user")
        if action == "Sign Up":
            # get form
            fname = request.form.get("fname")
            lname = request.form.get("lname")
            email = request.form.get("email")
            password = request.form.get("password")
            
            # create the user
            new_user = User(fname, lname, email, password)
            success = new_user.save()
            
            # was user created succesfully
            if success:
                logged_in_user = User.find_by_credentials(email, password)
                if logged_in_user:
                    session['user_profile'] = (logged_in_user.user_id, logged_in_user.fname, logged_in_user.lname, logged_in_user.email)
                    flash('Account created!', "success")
                    return redirect(url_for('dashboard'))
                else:
                    flash("Account was created but login failed", "danger")
            else:
                flash("Account was not created successfully, email might already exist", "danger")  

    return render_template("signup.html")
        

# logout 
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))

@app.route('/search/<name>')
def get_stock_name(name):
    list = []
    try:
       res = finnhub_client.symbol_lookup(name)
       # verify if anything was returned first
       if res['count'] > 0:
           list.append(res['result'])
           return jsonify({
               "Search Results": list
           })
       else:
           return jsonify({"message": "No matching stocks found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
        

if __name__ == '__main__':
    app.debug=True
    app.run()

# different tabs for all, stock, etf, index, mutual fund, currency
# search based on filter