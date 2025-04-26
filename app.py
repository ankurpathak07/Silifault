from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'tiff'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max upload
app.config['SECRET_KEY'] = os.urandom(24)  # Required for flash messages

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/features')
def features():
    return render_template('features.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Validate form data
        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        try:
            # In a real application, you would send an email here
            # For demo purposes, we'll just log the message
            print(f"Contact form submission: {name} <{email}> - {subject}")
            print(f"Message: {message}")
            
            # Return success response
            return jsonify({'success': True, 'message': 'Your message has been sent successfully'})
            
        except Exception as e:
            print(f"Error sending contact form: {str(e)}")
            return jsonify({'success': False, 'error': 'An error occurred while sending your message'}), 500
    
    # GET request - render the contact page
    return render_template('contact.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if the file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload JPG, PNG, or TIFF files only.'}), 400
        
        try:
            # Generate a unique filename to prevent overwriting
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Save the file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Here you would process the image with your AI model
            # For demo purposes, we'll return dummy data
            analysis_results = {
                'edge_defects': 2,
                'scratch_defects': 1,
                'donut_defects': 'None',
                'random_defects': 3,
                'confidence': 85,
                'image_path': url_for('static', filename=f'uploads/{unique_filename}')
            }
            
            # Store the results in the session for the results page
            session['analysis_results'] = analysis_results
            
            return jsonify(analysis_results)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # GET request - render the upload page
    return render_template('upload.html')


@app.route('/results')
def results():
    # Check if we have analysis results in the session
    if 'analysis_results' not in session:
        flash('No analysis results found. Please upload an image first.', 'error')
        return redirect(url_for('upload'))
    
    return render_template('results.html', results=session['analysis_results'])


@app.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        # Here you would generate a PDF report based on analysis results
        # For now, we'll just return a success message
        
        # In a real app, you might use a library like ReportLab to create a PDF
        # and then return it with send_file
        
        return jsonify({
            'message': 'Report generated successfully',
            'download_url': url_for('download_report')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download-report')
def download_report():
    # In a real app, you would generate a PDF here
    # For now, we'll just return a placeholder message
    return "Report download functionality will be implemented here"


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)