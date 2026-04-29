from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, Choice, Question, Submission


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission(enrollment=enrollment)
    submission.save()
    selected_ids = request.POST.getlist('choice')
    selected_choices = Choice.objects.filter(id__in=selected_ids)
    submission.choices.set(selected_choices)
    submission.save()
    return redirect('onlinecourse:show_exam_result', course_id=course_id, submission_id=submission.id)


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = submission.choices.values_list('id', flat=True)

    total_score = 0
    for question in course.question_set.all():
        q_selected = [cid for cid in selected_ids if question.choice_set.filter(id=cid).exists()]
        if question.is_get_score(q_selected):
            total_score += question.grade

    context = {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids,
        'total_score': total_score,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
