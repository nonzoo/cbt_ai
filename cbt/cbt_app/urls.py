from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('chat/', views.chat_view, name='chat'),
    path('questions/<int:exam_id>/<int:question_num>/', views.get_question),
    path('check_answer/<int:exam_id>/<int:question_num>/', views.check_answer),
    path('save_result/<int:exam_id>/', views.save_exam_result),
    path('count/<int:exam_id>/count/', views.exam_question_count),
    
]
