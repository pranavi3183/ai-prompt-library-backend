import json, redis
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Prompt, Tag

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)
REDIS_AVAILABLE = True
try:
    redis_client.ping()
except Exception:
    REDIS_AVAILABLE = False

def get_view_count(prompt_id):
    if not REDIS_AVAILABLE: return 0
    try:
        count = redis_client.get(f'prompt:views:{prompt_id}')
        return int(count) if count else 0
    except: return 0

def increment_view_count(prompt_id):
    if not REDIS_AVAILABLE: return 0
    try:
        return redis_client.incr(f'prompt:views:{prompt_id}')
    except: return 0

@method_decorator(csrf_exempt, name='dispatch')
class PromptListView(View):
    def get(self, request):
        tag_filter = request.GET.get('tag')
        prompts = Prompt.objects.prefetch_related('tags').all()
        if tag_filter:
            prompts = prompts.filter(tags__name__iexact=tag_filter)
        return JsonResponse([p.to_dict(view_count=get_view_count(p.id)) for p in prompts], safe=False)

    def post(self, request):
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        title = body.get('title', '').strip()
        content = body.get('content', '').strip()
        complexity = body.get('complexity')
        tag_names = body.get('tags', [])

        errors = {}
        if not title or len(title) < 3:
            errors['title'] = 'Title must be at least 3 characters.'
        if not content or len(content) < 20:
            errors['content'] = 'Content must be at least 20 characters.'
        if complexity is None or not isinstance(complexity, int) or not (1 <= complexity <= 10):
            errors['complexity'] = 'Complexity must be an integer between 1 and 10.'
        if errors:
            return JsonResponse({'errors': errors}, status=400)

        prompt = Prompt.objects.create(title=title, content=content, complexity=complexity)
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
                prompt.tags.add(tag)

        return JsonResponse(prompt.to_dict(), status=201)

@method_decorator(csrf_exempt, name='dispatch')
class PromptDetailView(View):
    def get(self, request, pk):
        try:
            prompt = Prompt.objects.prefetch_related('tags').get(pk=pk)
        except Prompt.DoesNotExist:
            return JsonResponse({'error': 'Prompt not found'}, status=404)
        view_count = increment_view_count(prompt.id)
        return JsonResponse(prompt.to_dict(view_count=view_count))

@method_decorator(csrf_exempt, name='dispatch')
class TagListView(View):
    def get(self, request):
        tags = Tag.objects.all().order_by('name')
        return JsonResponse([t.to_dict() for t in tags], safe=False)