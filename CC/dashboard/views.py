from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
import csv
import json
from .models import Notification
from issues.models import Issue
from accounts.decorators import student_required, admin_required, maintenance_required


@login_required
def dashboard_redirect(request):
    """Redirect to role-specific dashboard."""
    from django.shortcuts import redirect
    if request.user.role == 'admin':
        return redirect('dashboard:admin_dashboard')
    if request.user.role == 'maintenance':
        return redirect('dashboard:maintenance_dashboard')
    return redirect('dashboard:student_dashboard')


@student_required
def student_dashboard(request):
    """Student dashboard with their issues."""
    user = request.user
    issues = Issue.objects.filter(reported_by=user).order_by('-created_at')[:10]
    pending = Issue.objects.filter(reported_by=user, status='pending').count()
    in_progress = Issue.objects.filter(reported_by=user, status='in_progress').count()
    resolved = Issue.objects.filter(reported_by=user, status='resolved').count()
    return render(request, 'dashboard/student_dashboard.html', {
        'issues': issues,
        'pending': pending, 'in_progress': in_progress, 'resolved': resolved
    })


@admin_required
def admin_dashboard(request):
    """Admin dashboard with all issues and filters."""
    issues = Issue.objects.all().order_by('-created_at')
    category = request.GET.get('category')
    priority = request.GET.get('priority')
    status = request.GET.get('status')
    if category:
        issues = issues.filter(category=category)
    if priority:
        issues = issues.filter(priority=priority)
    if status:
        issues = issues.filter(status=status)
    issues = issues[:20]
    total = Issue.objects.count()
    pending = Issue.objects.filter(status='pending').count()
    in_progress = Issue.objects.filter(status='in_progress').count()
    resolved = Issue.objects.filter(status='resolved').count()
    return render(request, 'dashboard/admin_dashboard.html', {
        'issues': issues, 'total': total,
        'pending': pending, 'in_progress': in_progress, 'resolved': resolved
    })


@maintenance_required
def maintenance_dashboard(request):
    """Maintenance staff dashboard."""
    user = request.user
    assigned = Issue.objects.filter(assigned_to=user).order_by('-created_at')
    unassigned = Issue.objects.filter(assigned_to__isnull=True).order_by('-created_at')[:10]
    return render(request, 'dashboard/maintenance_dashboard.html', {
        'assigned': assigned, 'unassigned': unassigned
    })


@admin_required
def analytics(request):
    """Analytics page with charts data."""
    # Category distribution
    category_data = Issue.objects.values('category').annotate(count=Count('id')).order_by('-count')
    # Monthly trend (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_raw = list(Issue.objects.filter(created_at__gte=six_months_ago).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('id')).order_by('month'))
    monthly = [{'month': (m['month'].strftime('%Y-%m') if m.get('month') else ''), 'count': m['count']} for m in monthly_raw]
    # Average resolution time (approximate for SQLite)
    resolved_issues = Issue.objects.filter(status='resolved', resolved_at__isnull=False)
    avg_resolution_hours = 0
    if resolved_issues.exists():
        total_seconds = 0
        for i in resolved_issues:
            delta = i.resolved_at - i.created_at
            total_seconds += delta.total_seconds()
        avg_resolution_hours = total_seconds / resolved_issues.count() / 3600
    # Resolution rate
    total = Issue.objects.count()
    resolved_count = Issue.objects.filter(status='resolved').count()
    resolution_rate = (resolved_count / total * 100) if total > 0 else 0
    # Staff performance
    staff_perf = Issue.objects.filter(assigned_to__isnull=False, status='resolved').values(
        'assigned_to__username', 'assigned_to__first_name', 'assigned_to__last_name'
    ).annotate(resolved=Count('id')).order_by('-resolved')[:10]
    return render(request, 'dashboard/analytics.html', {
        'category_data': json.dumps(list(category_data)),
        'monthly_data': json.dumps(monthly),
        'avg_resolution_hours': round(avg_resolution_hours, 2),
        'resolution_rate': round(resolution_rate, 1),
        'staff_perf': staff_perf,
    })


@admin_required
def export_reports(request):
    """Export issues as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="campuscare_issues.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Title', 'Category', 'Priority', 'Status', 'Location', 'Reported By',
        'Assigned To', 'Created', 'Resolved', 'Resolution Notes'
    ])
    for issue in Issue.objects.all():
        writer.writerow([
            issue.id, issue.title, issue.get_category_display(), issue.get_priority_display(),
            issue.get_status_display(), f"{issue.location_building} {issue.location_room}".strip(),
            issue.reported_by.username, issue.assigned_to.username if issue.assigned_to else '',
            issue.created_at, issue.resolved_at or '', issue.resolution_notes or ''
        ])
    return response


@login_required
@require_GET
def notifications_api(request):
    """AJAX endpoint for real-time notifications."""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:15]
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'link': n.link,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat(),
    } for n in notifs]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'notifications': data, 'unread_count': unread_count})


@login_required
@require_GET
def mark_notification_read(request):
    """Mark notification as read."""
    nid = request.GET.get('id')
    if nid:
        Notification.objects.filter(user=request.user, id=nid).update(is_read=True)
    return JsonResponse({'ok': True})
