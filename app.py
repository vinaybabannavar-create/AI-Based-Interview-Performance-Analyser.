from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

from config import Config
from modules import db as db_module
from modules import utils
from modules.face_analysis import analyze_video_eye_and_expression
from modules.voice_analysis import analyze_audio_confidence
from modules.nlp_analysis import evaluate_answer_quality
from modules.scoring import compute_final_score
from modules.pdf_report import generate_pdf_from_report  
app = Flask(__name__)
app.config.from_object("config.Config")
app.secret_key = app.config['SECRET_KEY']

db_module.create_tables()


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not (name and email and password):
            flash("All fields are required", "error")
            return redirect(url_for('signup'))

        hashed = generate_password_hash(password)
        conn = db_module.get_conn()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
                        (name, email, hashed))
            conn.commit()
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for('login'))

        except:
            flash("Email already exists!", "error")
            return redirect(url_for('signup'))

        finally:
            conn.close()

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        conn = db_module.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "error")

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('user_name'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        if 'video' not in request.files:
            flash("No video file selected", "error")
            return redirect(request.url)

        file = request.files['video']

        if file.filename == '':
            flash("No selected file", "error")
            return redirect(request.url)

        if file and utils.allowed_file(file.filename):

           
            video_path = utils.save_uploaded_file(file)

           
            os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
            audio_out = os.path.join(app.config['AUDIO_FOLDER'],
                                     os.path.splitext(os.path.basename(video_path))[0] + ".wav")

            extracted = utils.extract_audio_from_video(video_path, audio_out)

            if extracted is None:
                flash("Audio extraction failed. Install FFmpeg!", "error")
                return redirect(request.url)

          
            face_metrics = analyze_video_eye_and_expression(video_path)
            audio_metrics = analyze_audio_confidence(audio_out)

            transcript = request.form.get('transcript', "")
            nlp_metrics = evaluate_answer_quality(
                transcript, expected_keywords=["API", "endpoint", "response"]
            )

            final_score = compute_final_score(face_metrics, audio_metrics, nlp_metrics)

           
            report = {
                "face": face_metrics,
                "audio": audio_metrics,
                "nlp": nlp_metrics,
                "final_score": final_score
            }

           
            os.makedirs("results/reports", exist_ok=True)
            json_path = os.path.join("results/reports", f"report_user{session['user_id']}.json")

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

           
            pdf_path = os.path.join("results/reports", f"report_user{session['user_id']}.pdf")
            generate_pdf_from_report(report, pdf_path)

           
            conn = db_module.get_conn()
            cur = conn.cursor()
            cur.execute("INSERT INTO results(user_id, report_path, json_report) VALUES (?, ?, ?)",
                        (session['user_id'], video_path, json.dumps(report)))
            conn.commit()
            conn.close()

          
            return render_template(
                'result.html',
                report=report,
                username=session.get('user_name')
            )

    return render_template('upload.html')



@app.route('/results/<filename>')
def results_file(filename):
    return send_from_directory("results/reports", filename, as_attachment=True)


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    return redirect(url_for('login'))

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
