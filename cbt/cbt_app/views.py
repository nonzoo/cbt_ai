from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Question
from .serializers import QuestionSerializer
from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

BACKEND_LOGIN_URL = 'http://localhost:8000/api/token/' 

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        response = requests.post(BACKEND_LOGIN_URL, json={
            'username': username,
            'password': password
        })

        if response.status_code == 200:
            token = response.json().get('access')
            return redirect(f'/api/chat/?token={token}')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

@permission_classes([IsAuthenticated])
def chat_view(request):
    token = request.GET.get('token', '')
    return render(request, 'chat.html', {'token': token})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question(request, exam_id, question_num):
    try:
        question = Question.objects.filter(exam_id=exam_id)[question_num]
        serializer = QuestionSerializer(question)
        return Response(serializer.data)
    except IndexError:
        return Response({"error": "No more questions"}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_answer(request, exam_id, question_num):
    question = Question.objects.filter(exam_id=exam_id)[question_num]
    user_answer = int(request.data.get("answer"))
    is_correct = (user_answer == question.correct_option)
    return Response({"is_correct": is_correct, "correct_answer": question.correct_option})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_question_count(request, exam_id):
    count = Question.objects.filter(exam_id=exam_id).count()
    return Response({"count": count})