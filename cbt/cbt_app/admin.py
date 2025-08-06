from django.contrib import admin
from .models import Exam, Question, ExamSession

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'text', 'correct_option')
    list_filter = ('exam',)
    search_fields = ('text',)

@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'exam', 'current_question', 'score')
    list_filter = ('user', 'exam')
    search_fields = ('user__username', 'exam__name')