from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('topic/<int:topic_id>/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('leaderboard/<int:quiz_id>/', views.leaderboard_view, name='leaderboard'),
    path('review/<int:quiz_id>/', views.review_quiz, name='review_quiz'),
    path('leaderboard/global/', views.global_leaderboard_view, name='global_leaderboard'),

]
