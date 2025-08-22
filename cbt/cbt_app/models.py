from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
    name = models.CharField(max_length=100)
    duration_minutes = models.PositiveIntegerField(default=120) 
    def __str__(self):
        return self.name

class Question(models.Model):
    DIFFICULTY_CHOICES = (
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.IntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')])
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=2)
    topic = models.CharField(max_length=100, blank=True) 
    def __str__(self):
        return self.text

class ExamSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    asked_question_ids = models.JSONField(default=list, blank=True)
    current_difficulty = models.PositiveSmallIntegerField(default=2)
    correct_streak = models.PositiveSmallIntegerField(default=0)
    incorrect_streak = models.PositiveSmallIntegerField(default=0)
    adaptive = models.BooleanField(default=True)
    pending_question_id = models.IntegerField(null=True, blank=True) 
    started_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)

    # legacy count-based fields
    current_question = models.IntegerField(default=0)
    score = models.IntegerField(default=0)