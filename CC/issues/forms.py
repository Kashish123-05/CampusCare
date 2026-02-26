from django import forms
from .models import Issue


ALLOWED_IMAGE_TYPES = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


class IssueForm(forms.ModelForm):
    """Form for students to submit issues."""
    class Meta:
        model = Issue
        fields = ['title', 'description', 'category', 'priority', 'image', 'location_building', 'location_room']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief title for the issue'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the issue in detail'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'location_building': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Building name'}),
            'location_room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room number'}),
        }

    def clean_image(self):
        img = self.cleaned_data.get('image')
        if img:
            if img.content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError('Please upload a valid image (JPEG, PNG, GIF, WebP).')
            if img.size > MAX_IMAGE_SIZE:
                raise forms.ValidationError('Image size must be under 5MB.')
        return img


class IssueAssignForm(forms.ModelForm):
    """Form for admin to assign issues."""
    class Meta:
        model = Issue
        # Only allow admin to change assignee and priority from this section
        fields = ['assigned_to', 'priority']
        widgets = {
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import User
        self.fields['assigned_to'].queryset = User.objects.filter(role='maintenance').order_by('username')
        self.fields['assigned_to'].required = False


class IssueStatusForm(forms.ModelForm):
    """Form for maintenance staff to update status."""
    class Meta:
        model = Issue
        fields = ['status', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add resolution notes when resolving'}),
        }
