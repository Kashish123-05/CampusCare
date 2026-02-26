"""Email and notification helpers for issues."""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from dashboard.models import Notification


def notify_user(user, title, message, link=''):
    """Create in-app notification for user."""
    Notification.objects.create(user=user, title=title, message=message, link=link)


def send_issue_submitted_email(issue):
    """Email when issue is submitted."""
    try:
        send_mail(
            subject=f'[CampusCare] Issue Reported: {issue.title}',
            message=f'Your issue "{issue.title}" has been submitted successfully. We will look into it shortly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[issue.reported_by.email],
            fail_silently=True,
        )
    except Exception:
        pass


def send_issue_assigned_email(issue):
    """Email when issue is assigned to staff."""
    try:
        send_mail(
            subject=f'[CampusCare] Issue Assigned: {issue.title}',
            message=f'Issue "{issue.title}" has been assigned to maintenance staff.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[issue.reported_by.email],
            fail_silently=True,
        )
        if issue.assigned_to and issue.assigned_to.email:
            send_mail(
                subject=f'[CampusCare] New Assignment: {issue.title}',
                message=f'You have been assigned to resolve: {issue.title}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[issue.assigned_to.email],
                fail_silently=True,
            )
    except Exception:
        pass


def send_status_changed_email(issue, old_status, new_status):
    """Email when issue status changes."""
    try:
        send_mail(
            subject=f'[CampusCare] Status Update: {issue.title} - {new_status}',
            message=f'Your issue "{issue.title}" status has been updated from {old_status} to {new_status}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[issue.reported_by.email],
            fail_silently=True,
        )
    except Exception:
        pass


def send_issue_resolved_email(issue):
    """Email when issue is resolved."""
    try:
        send_mail(
            subject=f'[CampusCare] Issue Resolved: {issue.title}',
            message=f'Your issue "{issue.title}" has been resolved. Resolution notes: {issue.resolution_notes or "N/A"}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[issue.reported_by.email],
            fail_silently=True,
        )
    except Exception:
        pass
