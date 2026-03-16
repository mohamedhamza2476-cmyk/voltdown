from flask import Flask, render_template, request, jsonify, Response
import yt_dlp
import requests
from urllib.parse import quote

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_video():
    video_url = request.form.get('url')
    if not video_url: return jsonify({"error": "يرجى إدخال الرابط"}), 400
    try:
        ydl_opts = {'quiet': True, 'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats_list = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    formats_list.append({'quality': f.get('resolution') or f.get('format_note'), 'ext': f.get('ext'), 'url': f.get('url')})
            return jsonify({"title": info.get('title'), "thumb": info.get('thumbnail'), "formats": formats_list[::-1]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    filename = request.args.get('filename', 'video.mp4')
    req = requests.get(video_url, stream=True)
    def generate():
        for chunk in req.iter_content(chunk_size=1024*1024): yield chunk
    return Response(generate(), headers={"Content-Type": "application/octet-stream", "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"})

# بدلاً من app.run()، بنسيب app بس عشان Vercel يشوفه
app.debug = True

# لازم نتأكد إننا بنصدر الـ app كمتغير رئيسي
application = app
