from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from openai import OpenAI
import google.generativeai as genai
import os
import markdown
from flask_sqlalchemy import SQLAlchemy
from form import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import re

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False


genai.configure(api_key= os.getenv("GOOGLE_API_KEY"))

app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://postgres:chit7126@localhost:5432/aidictionary"
app.config["SQLALCHEMY_TRACK_MODIFICATION"]=False
print(app.config["SQLALCHEMY_DATABASE_URI"])
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable= False)
    password = db.Column(db.String(200), nullable=False)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable =False)
    meaning = db.Column(db.Text)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.id"))

with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit(): 
        user_email = form.email.data
        user_pass = form.password.data
        hashed_pass = generate_password_hash(user_pass)
        new_email = Users(email = user_email, password= hashed_pass)
        db.session.add(new_email)
        db.session.commit()

        flash("Registration Successfull, Please Login!", "success")
        return redirect(url_for("login"))
        
        
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET" , "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_email = form.email.data
        user = Users.query.filter_by(email=user_email).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                session["user_id"] = user.id
                session["user_email"]= user.email
                flash("You're Logged In", "success")
                return redirect(url_for("home"))
                
            else:
                flash("Incorrect Password", "warning")
                return render_template("login.html", form=form)
                
        else:
            flash("Please Register First", "success")
            return render_template("login.html", form=form)
    else:       
        return render_template("login.html", form=form)  

    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
    
    
@app.route("/home")
def home():
    if "user_id" not in session:
        flash("Login First", "error")
        return redirect(url_for("login"))
    return render_template("home.html")
   

@app.route("/api/learned_words")
def learned_words():
    if "user_id" not in session:
        return {"words": []}
    words = Word.query.filter_by(user_id = session["user_id"]).all()
    word_list = []

    for w in words: 
        word_list.append(w.word)
    return{"words": word_list}

@app.route("/api", methods=["POST"])
def api():

    if "user_id" not in session:
        return {"error": "not logged in "}
        
    data = request.json
    word_text = data["text"]
    word_text = "".join(word_text.strip().split()).lower()
    if not re.match(r"^[a-zA-Z]+( [a-zA-Z]+)?$", word_text):
        return jsonify({"error" : "only letters are allowed"}), 400
    
    words = Word.query.filter_by(user_id=session["user_id"]).order_by(Word.id.desc()).limit(20).all()
    learned_words = [w.word for w in words]
    word = data["text"]

    existing = Word.query.filter_by(
        word= word_text,
        user_id=session["user_id"]
    ).first()
    if existing:
        return{"html": existing.meaning,
               "learned_words": learned_words}
    try:
        
        model = genai.GenerativeModel("gemini-3-flash-preview")
        prompt = f"""
                    "role": "system",
                    "content": "you are an English dictionary engine. Always return the result in the EXACT structure below - no extra sentences, no greetings , no explanation."
                    "STRICT RULES:"
                    "- Do NOT add intro text or something or explanation"
                    "- DO NOT write paragraph or combine lines"
                    "- Each synonym MUST be on its own line with'-'."
                    "- Each example sentence must be on its own new line with'-'."
                    "-START directly with '###Word'."
                    "- GIve answer only in the format given below"
                    "- Put next line when told to do so"
                    "Format:"
                    {word_text}

                    "###Synonyms:"
                    
                    "-synonym1"

                    "-synonym2"

                    "-synonym3"

                    "###Meaning:"
                    
                    "meaning"
                    
                    "###Example Sentence:"
                    
                    "- example sentence 1"

                    "- example sentence 2"
                
                """
        response = model.generate_content(prompt)
        raw = response.text
        html = markdown.markdown(raw)
        new_data = Word(word=word_text, meaning=html, user_id= session["user_id"])
        db.session.add(new_data)
        db.session.commit()

        words = Word.query.filter_by(user_id=session["user_id"]).order_by(Word.id.desc()).limit(20).all()
        learned_words = [w.word for w in words]
        word = data["text"]
        return {
                "html": html,
                "learned_words": learned_words  } 
   
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "API Fallback Failure, Try Again Later"}), 500


    
 
if __name__ == "__main__":
    app.run(debug=True)

   

    