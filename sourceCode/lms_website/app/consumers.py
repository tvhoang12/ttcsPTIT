import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from .models import Blog, BlogComment
from django.contrib.auth import get_user_model

User = get_user_model()

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.blog_id = self.scope['url_route']['kwargs']['blog_id']
        self.room_group_name = f'blog_{self.blog_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data['content']
        parent_id = data.get('parent_id')
        user_id = self.scope['user'].id

        # Lưu comment vào DB (nên kiểm tra quyền user ở đây)
        blog = await Blog.objects.aget(pk=self.blog_id)
        user = await User.objects.aget(pk=user_id)
        comment = BlogComment(blog=blog, user=user, content=content)
        if parent_id:
            comment.parent_id = parent_id
        await comment.asave()

        # Render lại comments-list
        comments = await BlogComment.objects.filter(blog=blog, parent__isnull=True).order_by('-created_at').aall()
        html = render_to_string('app/comments_list.html', {'comments': comments, 'user': user})

        # Gửi tới tất cả client trong group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_comment',
                'html': html,
            }
        )

    async def send_comment(self, event):
        html = event['html']
        await self.send(text_data=json.dumps({'comments_html': html}))