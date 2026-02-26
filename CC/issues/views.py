from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Issue, IssueHistory
from .forms import IssueForm, IssueAssignForm, IssueStatusForm
from .utils import (
    notify_user, send_issue_submitted_email, send_issue_assigned_email,
    send_status_changed_email, send_issue_resolved_email
)
from accounts.decorators import student_required, admin_required, maintenance_required
from accounts.models import User


@login_required
def issue_list(request):
    """List issues - filtered by user role."""
    user = request.user
    if user.role == 'admin':
        issues = Issue.objects.all()
    elif user.role == 'maintenance':
        issues = Issue.objects.filter(assigned_to=user) | Issue.objects.filter(assigned_to__isnull=True)
    else:
        issues = Issue.objects.filter(reported_by=user)

    category = request.GET.get('category')
    priority = request.GET.get('priority')
    status = request.GET.get('status')
    if category:
        issues = issues.filter(category=category)
    if priority:
        issues = issues.filter(priority=priority)
    if status:
        issues = issues.filter(status=status)

    return render(request, 'issues/issue_list.html', {
        'issues': issues,
        'issue_category_choices': Issue.CATEGORY_CHOICES
    })


@student_required
def issue_create(request):
    """Students submit new issues."""
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.reported_by = request.user
            issue.save()
            notify_user(request.user, 'Issue Submitted', f'Your issue "{issue.title}" has been submitted.', f'/issues/{issue.id}/')
            send_issue_submitted_email(issue)
            messages.success(request, 'Issue submitted successfully!')
            return redirect('issues:issue_detail', pk=issue.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = IssueForm()
    return render(request, 'issues/issue_form.html', {'form': form, 'action': 'Submit'})


@login_required
def issue_detail(request, pk):
    """View issue details."""
    issue = get_object_or_404(Issue, pk=pk)
    user = request.user
    if user.role == 'student' and issue.reported_by != user:
        messages.error(request, 'You do not have permission to view this issue.')
        return redirect('issues:issue_list')
    if user.role == 'maintenance' and issue.assigned_to != user and issue.assigned_to:
        messages.error(request, 'You do not have permission to view this issue.')
        return redirect('issues:issue_list')

    assign_form = IssueAssignForm(instance=issue) if user.role == 'admin' else None
    status_form = IssueStatusForm(instance=issue) if user.role in ('admin', 'maintenance') else None
    return render(request, 'issues/issue_detail.html', {
        'issue': issue, 'assign_form': assign_form, 'status_form': status_form
    })


@admin_required
def issue_assign(request, pk):
    """Admin assigns issue to staff."""
    issue = get_object_or_404(Issue, pk=pk)
    if request.method == 'POST':
        form = IssueAssignForm(request.POST, instance=issue)
        if form.is_valid():
            old_assigned = issue.assigned_to
            form.save()
            if issue.assigned_to != old_assigned:
                notify_user(issue.reported_by, 'Issue Assigned', f'Issue "{issue.title}" has been assigned.', f'/issues/{issue.id}/')
                if issue.assigned_to:
                    notify_user(issue.assigned_to, 'New Assignment', f'You have been assigned: {issue.title}', f'/issues/{issue.id}/')
                send_issue_assigned_email(issue)
            messages.success(request, 'Issue updated.')
    return redirect('issues:issue_detail', pk=pk)


@maintenance_required
def issue_update_status(request, pk):
    """Maintenance staff updates issue status."""
    issue = get_object_or_404(Issue, pk=pk)
    if issue.assigned_to != request.user and request.user.role != 'admin':
        messages.error(request, 'Permission denied.')
        return redirect('issues:issue_list')
    if request.method == 'POST':
        form = IssueStatusForm(request.POST, instance=issue)
        if form.is_valid():
            old_status = issue.status
            issue = form.save(commit=False)
            if form.cleaned_data['status'] == 'resolved':
                from django.utils import timezone
                issue.resolved_at = timezone.now()
                issue.resolution_notes = form.cleaned_data.get('resolution_notes', '') or issue.resolution_notes
            issue.save()
            IssueHistory.objects.create(
                issue=issue, old_status=old_status, new_status=issue.status,
                changed_by=request.user, notes=issue.resolution_notes or ''
            )
            notify_user(issue.reported_by, 'Status Update', f'Issue "{issue.title}" is now {issue.status}.', f'/issues/{issue.id}/')
            send_status_changed_email(issue, old_status, issue.status)
            if issue.status == 'resolved':
                send_issue_resolved_email(issue)
            messages.success(request, 'Status updated.')
    return redirect('issues:issue_detail', pk=pk)
