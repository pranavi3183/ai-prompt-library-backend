from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self): return self.name
    def to_dict(self): return {'id': self.id, 'name': self.name}

class Prompt(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    complexity = models.IntegerField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='prompts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self): return self.title

    def to_dict(self, view_count=0):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'complexity': self.complexity,
            'tags': [tag.to_dict() for tag in self.tags.all()],
            'view_count': view_count,
            'created_at': self.created_at.isoformat(),
        }