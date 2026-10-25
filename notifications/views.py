import json
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from notifications.models import Trigger, NotificationTemplate, ChannelType, NotificationLog
from notifications.services.dispatcher import NotificationDispatcher

def admin_matrix_view(request):
    triggers = Trigger.objects.all().order_by('id')
    # WhatsApp commented out - showing Email and Web Push
    channels = [ChannelType.EMAIL, ChannelType.WEB_PUSH]

    matrix_data = []
    for trigger in triggers:
        channel_cells = {}
        for ch in channels:
            template, _ = NotificationTemplate.objects.get_or_create(
                trigger=trigger,
                channel=ch,
                defaults={'title': f"{trigger.name} Notification", 'body': 'Default template body', 'is_enabled': True}
            )
            channel_cells[ch] = template
        matrix_data.append({
            'trigger': trigger,
            'cells': channel_cells
        })

    recent_logs = NotificationLog.objects.order_by('-sent_at')[:15]
    return render(request, 'notifications/matrix.html', {
        'matrix_data': matrix_data,
        'channels': channels,
        'logs': recent_logs,
        'test_email': os.getenv('TEST_RECIPIENT_EMAIL', ''),
        'onesignal_app_id': os.getenv('ONESIGNAL_APP_ID', '88dc746e-7ac3-437b-b102-1d249a19b7f4'),
    })

@csrf_exempt
def toggle_template_api(request, template_id):
    if request.method == "POST":
        tmpl = get_object_or_404(NotificationTemplate, id=template_id)
        tmpl.is_enabled = not tmpl.is_enabled
        tmpl.save()
        return JsonResponse({'success': True, 'is_enabled': tmpl.is_enabled})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def save_template_api(request, template_id):
    if request.method == "POST":
        tmpl = get_object_or_404(NotificationTemplate, id=template_id)
        data = json.loads(request.body)
        tmpl.title = data.get('title', tmpl.title)
        tmpl.body = data.get('body', tmpl.body)
        tmpl.save()
        return JsonResponse({'success': True, 'message': 'Template updated successfully'})
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def test_send_api(request, template_id):
    if request.method == "POST":
        tmpl = get_object_or_404(NotificationTemplate, id=template_id)
        result = NotificationDispatcher.dispatch_single_template(
            tmpl,
            context={"username": "CandidateUser"}
        )
        return JsonResponse({
            'success': True, 
            'channel': tmpl.channel,
            'title': tmpl.title or f"{tmpl.trigger.name} Alert",
            'body': tmpl.body.replace("{{username}}", "CandidateUser"),
            'result': result
        })
    return JsonResponse({'error': 'Invalid method'}, status=405)

def fire_manual_trigger(request, slug):
    NotificationDispatcher.dispatch_trigger(slug, context={"username": "CandidateUser"})
    return redirect('admin_matrix')
