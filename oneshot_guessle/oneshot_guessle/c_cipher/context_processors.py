from django.db.models import Count
from .models import Submission


def c_cipher_scores(request):
    """Add user puzzle scores to all c_cipher templates."""
    context = {
        'year_score': 0,
        'total_score': 0,
    }
    
    if request.user.is_authenticated:
        # Get the latest hijri_year (assuming 1447 for now, update as needed)
        latest_hijri_year = 1447
        
        context['year_score'] = Submission.objects.filter(
            user=request.user,
            is_correct=True,
            puzzle__hijri_year=latest_hijri_year
        ).count()
        
        context['total_score'] = Submission.objects.filter(
            user=request.user,
            is_correct=True
        ).count()
    
    return context
