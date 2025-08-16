# views.py
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Question, Exam, ExamSession
from .serializers import QuestionSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import requests

BACKEND_LOGIN_URL = 'http://localhost:8000/api/token/'

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        resp = requests.post(BACKEND_LOGIN_URL, json={'username': username, 'password': password})
        if resp.status_code == 200:
            token = resp.json().get('access')

            # create Django session so @login_required passes
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

            return redirect(f'/api/chat/?token={token}')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

@login_required
def chat_view(request):
    username = request.user.username
    token = request.GET.get('token', '')
    return render(request, 'chat.html', {'token': token, 'username': username})




def _next_difficulty(current: int, got_it_right: bool) -> int:
    if got_it_right:
        return min(3, current + 1)
    return max(1, current - 1)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def adaptive_next_question(request, exam_id: int):
   
    exam = Exam.objects.get(id=exam_id)
    session, _ = ExamSession.objects.get_or_create(
        user=request.user, exam=exam,
        defaults={'current_difficulty': 2, 'adaptive': True}
    )

    total_questions = Question.objects.filter(exam=exam).count()

    asked_count = len(session.asked_question_ids)
    if asked_count >= total_questions:
        return Response({"done": True, "message": "Exam complete.", "total_questions": total_questions}, status=200)

    # Pool: same difficulty first, fallback to any unanswered
    base_qs = Question.objects.filter(exam=exam).exclude(id__in=session.asked_question_ids)
    pool = base_qs.filter(difficulty=session.current_difficulty)
    if not pool.exists():
        pool = base_qs

    if not pool.exists():
        return Response({"done": True, "message": "No more questions.", "total_questions": total_questions}, status=200)

    question = random.choice(list(pool))

    # mark as asked
    session.asked_question_ids = session.asked_question_ids + [question.id]
    session.current_question = len(session.asked_question_ids)
    session.save()

    serializer = QuestionSerializer(question)
    return Response({
        "done": False,
        "question": serializer.data,
        "asked_count": session.current_question,
        "total_questions": total_questions,
        "current_difficulty": session.current_difficulty
    }, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def adaptive_check_answer(request):
    exam_id = int(request.data.get("exam_id"))
    question_id = int(request.data.get("question_id"))
    user_answer = int(request.data.get("answer"))

    exam = Exam.objects.get(id=exam_id)
    q = Question.objects.get(id=question_id, exam=exam)
    session, _ = ExamSession.objects.get_or_create(
        user=request.user, exam=exam,
        defaults={'current_difficulty': 2, 'adaptive': True}
    )

    total_questions = Question.objects.filter(exam=exam).count()

    is_correct = (user_answer == q.correct_option)
    if is_correct:
        session.score += 1
        session.correct_streak += 1
        session.incorrect_streak = 0
    else:
        session.incorrect_streak += 1
        session.correct_streak = 0

    session.current_difficulty = _next_difficulty(session.current_difficulty, is_correct)
    session.save()

    done = len(session.asked_question_ids) >= total_questions
    return Response({
        "is_correct": is_correct,
        "correct_answer": q.correct_option,
        "score": session.score,
        "asked_count": len(session.asked_question_ids),
        "total_questions": total_questions,           
        "current_difficulty": session.current_difficulty,
        "done": done
    }, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_exam_result(request, exam_id):
    try:
        score = int(request.data.get("score"))
        total_questions = int(request.data.get("total_questions"))
        exam = Exam.objects.get(id=exam_id)
        ExamSession.objects.update_or_create(
            user=request.user,
            exam=exam,
            defaults={'score': score, 'current_question': total_questions}
        )
        return Response({"status": "success"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)






# ---------- Existing classic endpoints (kept) ----------

"""@api_view(['GET'])
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
    return Response({"count": count})"""
