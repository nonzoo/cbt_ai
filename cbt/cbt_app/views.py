from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Question
from .serializers import QuestionSerializer

@api_view(['GET'])
def get_question(request, exam_id, question_num):
    try:
        question = Question.objects.filter(exam_id=exam_id)[question_num]
        serializer = QuestionSerializer(question)
        return Response(serializer.data)
    except IndexError:
        return Response({"error": "No more questions"}, status=404)

@api_view(['POST'])
def check_answer(request, exam_id, question_num):
    question = Question.objects.filter(exam_id=exam_id)[question_num]
    user_answer = int(request.data.get("answer"))
    is_correct = (user_answer == question.correct_option)
    return Response({"is_correct": is_correct, "correct_answer": question.correct_option})


@api_view(['GET'])
def exam_question_count(request, exam_id):
    count = Question.objects.filter(exam_id=exam_id).count()
    return Response({"count": count})