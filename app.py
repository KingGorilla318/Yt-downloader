from flask import Flask, render_template, request, redirect, url_for, send_file
from pytube import YouTube
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def clean_filename(filename):
    # Remove invalid characters from filename
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def cleanup_downloads_folder():
    # Delete contents of downloads folder
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print("An error occurred while deleting file:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        resolution = request.form.get('resolution', '720p')
        shorts = request.form.get('shorts') == 'on'
        if url:
            yt = YouTube(url)
            if shorts:
                video = yt.streams.filter(adaptive=True).first()
            else:
                if resolution == '720p':
                    video = yt.streams.filter(res="720p", progressive=True).first()
                elif resolution == '480p':
                    video = yt.streams.filter(res="480p", progressive=True).first()
                elif resolution == '360p':
                    video = yt.streams.filter(res="360p", progressive=True).first()
            if video:
                file_name = clean_filename(video.title) + '.mp4'  # Clean the filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                video.download(output_path=app.config['UPLOAD_FOLDER'], filename=file_name)
                response = send_file(file_path, as_attachment=True)  # Return file as attachment
                cleanup_downloads_folder()  # Clean up downloads folder
                return response
            else:
                return redirect(url_for('index', error="No video available for this URL."))
        else:
            return redirect(url_for('index', error="Please provide a valid URL."))
    except Exception as e:
        return redirect(url_for('index', error="An error occurred: " + str(e)))

if __name__ == '__main__':
    # Run the app on 0.0.0.0 with a specified port
    app.run(host='0.0.0.0', port=8080)
