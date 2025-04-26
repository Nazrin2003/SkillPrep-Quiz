from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import models

from .models import Topic, Quiz, Question, Choice, UserQuizResult
from .forms import SignUpForm
from .models import UserAnswer

def home(request):
    topics = Topic.objects.all()
    return render(request, 'core/home.html', {'topics': topics})

def quiz_list(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    quizzes = Quiz.objects.filter(topic=topic)
    return render(request, 'core/quiz_list.html', {'topic': topic, 'quizzes': quizzes})

def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz).prefetch_related('choice_set')

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for question in questions:
            selected = request.POST.get(str(question.id))
            if selected:
                selected_id = int(selected)
                selected_choice = Choice.objects.filter(id=selected_id, question=question).first()
                correct_choice = question.choice_set.filter(is_correct=True).first()

                is_correct = selected_choice == correct_choice

                # ✅ Save user's answer
                if request.user.is_authenticated:
                    UserAnswer.objects.create(
                        user=request.user,
                        quiz=quiz,
                        question=question,
                        selected_choice=selected_choice,
                        is_correct=is_correct
                    )

                if is_correct:
                    score += 1

        percent = (score / total) * 100

        # ✅ Save user result
        if request.user.is_authenticated:
            UserQuizResult.objects.create(
                user=request.user,
                quiz=quiz,
                score=percent
            )

        return render(request, 'core/result.html', {
            'score': percent,
            'quiz': quiz
        })

    return render(request, 'core/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })


# -----------------------------
# 🔐 LOGIN, SIGNUP, LOGOUT VIEWS
# -----------------------------

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    results = UserQuizResult.objects.filter(user=request.user).select_related('quiz')
    total_tests = results.count()
    average_score = results.aggregate(models.Avg('score'))['score__avg']

    return render(request, 'core/profile.html', {
        'results': results,
        'total_tests': total_tests,
        'average_score': round(average_score, 2)
    })


def leaderboard_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    top_scores = UserQuizResult.objects.filter(quiz=quiz).select_related('user').order_by('-score', 'completed_on')[:10]

    return render(request, 'core/leaderboard.html', {
        'quiz': quiz,
        'top_scores': top_scores
    })

@login_required
def review_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz).prefetch_related('choice_set')
    answers = UserAnswer.objects.filter(user=request.user, quiz=quiz)

    answer_dict = {answer.question_id: answer for answer in answers}

    return render(request, 'core/review.html', {
        'quiz': quiz,
        'questions': questions,
        'answer_dict': answer_dict
    })

