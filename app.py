from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Dummy admin credentials (replace with actual authentication)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/services")
def services():
    return render_template('services.html')

@app.route("/pricing")
def pricing():
    return render_template('pricing.html')

@app.route("/how-it-works")
def how_it_works():
    return render_template('how-it-works.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Generate a unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

            # Retrieve form data
            name = request.form['name']
            description = request.form['description']
            size = request.form['size']
            pieces = request.form['pieces']
            address = request.form['address']
            ewallet = request.form['ewallet']
            time = request.form['time']

            # Store form data along with the file path
            record = {
                'name': name,
                'description': description,
                'size': size,
                'pieces': pieces,
                'address': address,
                'ewallet': ewallet,
                'time': time,
                'file_path': unique_filename  # Save only the unique filename
            }

            # Save the record to a JSON file
            with open(os.path.join(app.config['UPLOAD_FOLDER'], 'records.json'), 'a') as f:
                f.write(json.dumps(record) + '\n')

            flash('File uploaded and details submitted successfully!')
            return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login successful!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' in session:
        # Fetch client uploads from the database
        client_uploads = []
        # Replace this with actual database query to fetch client uploads
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'records.json'), 'r') as f:
            for line in f:
                record = json.loads(line)
                client_uploads.append(record)
        return render_template('admin_dashboard.html', client_uploads=client_uploads)
    else:
        flash('Please login as admin to access this page.')
        return redirect(url_for('admin_login'))

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
