from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404 
import requests

from .models import Resource, Purchase, KS_CHOICES, CATEGORY_CHOICES, EXAM_B_CHOICES

# Create your views here.
def resources_page(request):
    # Get selected filters from request (assuming checkboxes are named accordingly)
    selected_keystage = request.GET.getlist('keystage')  # Can be a list of selected values
    selected_category = request.GET.getlist('category')
    selected_exam_board = request.GET.getlist('exam_board')

    # Filter resources based on selections
    resources = Resource.objects.all()
    if selected_keystage:
        resources = resources.filter(keystage__in=selected_keystage)
    if selected_category:
        resources = resources.filter(category__in=selected_category)
    if selected_exam_board:
        resources = resources.filter(exam_board__in=selected_exam_board)

    # Render the template with the filtered list
    context = {'resources': resources, 'ks_choices': KS_CHOICES, 'category_choices': CATEGORY_CHOICES, 'exam_b_choices': EXAM_B_CHOICES}
    return render(request, 'resource_list.html', context)

