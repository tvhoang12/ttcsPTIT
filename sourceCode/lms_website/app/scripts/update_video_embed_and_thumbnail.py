import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_website.settings')
django.setup()

from app.models import Video

def get_youtube_id(url):
    """
    Trích xuất video ID từ URL YouTube.
    """
    regex = (
        r'(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/ ]{11})'
    )
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def get_embed_code(video_id):
    return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'

def get_thumbnail_url(video_id):
    return f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'

def update_videos():
    videos = Video.objects.all()
    for video in videos:
        video_id = get_youtube_id(video.video_url)
        if video_id:
            video.embed_code = get_embed_code(video_id)
            # Nếu bạn có trường thumbnail trong model Video:
            # video.thumbnail = get_thumbnail_url(video_id)
            print(f"Updated: {video.title}")
            video.save()
        else:
            print(f"Skipped (invalid URL): {video.title}")

if __name__ == "__main__":
    update_videos()