from django import forms
from .models import Course, Blog, User, BlogComment, CourseCategory
from ckeditor_uploader.widgets import CKEditorUploadingWidget

LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]

class CourseForm(forms.ModelForm):
    level = forms.ChoiceField(choices=LEVEL_CHOICES, widget=forms.Select)
    categories = forms.ModelMultipleChoiceField(
        queryset=CourseCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Categories"
    )

    class Meta:
        model = Course
        fields = [
            'courseName', 'thumbnail', 'description', 'price', 'duration',
            'level', 'language', 'categories'
        ]

class BlogForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget(config_name='default'))
    class Meta:
        model = Blog
        fields = ['title', 'content']

ROLE_CHOICES = [
    ('student', 'student'),
    ('instructor', 'instructor'),
    ('admin', 'admin'),
]
class ProfileForm(forms.ModelForm):
    self_description = forms.CharField(widget=CKEditorUploadingWidget(config_name='default'), required=False)
    email = forms.EmailField(required=True, max_length=254)
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select)
    birthday = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = User
        fields = ['email', 'phone', 'birthday', 'avatar', 'role', 'self_description']

class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Nhập bình luận...', 'class': 'comment-input'}),
        }