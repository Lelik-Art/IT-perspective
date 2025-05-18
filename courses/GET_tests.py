from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Test, Question, Option, TestSettings

# 1. Список всех тестов (GET /tests/)
def test_list(request):
    tests = Test.objects.all()
    return render(request, 'tests/list.html', {'tests': tests})

# 2. Детали теста (GET /tests/<test_id>/)
def test_detail(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    questions = test.questions.all()
    settings = test.settings
    return render(request, 'tests/detail.html', {
        'test': test,
        'questions': questions,
        'settings': settings,
    })

# 3. Детали вопроса (GET /tests/<test_id>/questions/<question_id>/)
def question_detail(request, test_id, question_id):
    question = get_object_or_404(Question, pk=question_id, test_id=test_id)
    options = question.options.all()
    return render(request, 'tests/question.html', {
        'question': question,
        'options': options,
    })

# 4. Получить правильные ответы (GET /tests/<test_id>/questions/<question_id>/correct/)
def correct_answers(request, test_id, question_id):
    question = get_object_or_404(Question, pk=question_id, test_id=test_id)
    correct_options = question.options.filter(is_correct=True).values_list('id', flat=True)
    return JsonResponse({'correct_answers': list(correct_options)})

# 5. Максимальный балл за тест (GET /tests/<test_id>/max-score/)
def max_score(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    total_score = sum(q.points for q in test.questions.all())
    return JsonResponse({'max_score': total_score})