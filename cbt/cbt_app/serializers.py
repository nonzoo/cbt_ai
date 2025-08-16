# serializers.py
from rest_framework import serializers
from .models import Exam, Question, ExamSession

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'option1', 'option2', 'option3', 'option4', 'difficulty']  # +difficulty

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'name']

class ExamSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSession
        fields = ['id', 'user', 'exam', 'current_question', 'score', 'asked_question_ids',
                  'current_difficulty', 'correct_streak', 'incorrect_streak', 'adaptive', 'total_questions']
