from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.admin.utils import get_deleted_objects
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.template.response import SimpleTemplateResponse
from django.urls import path
from django.utils.encoding import force_str


from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'examNo', 'exam_yr']
    actions=['publish_blog','unpublish_blog']

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = [
            path(
                f'{info[1]}/bulk_update_exam_no/',
                self.admin_site.admin_view(self.bulk_update_exam_no),
                name=f'{info[0]}_{info[1]}_bulk_update_exam_no'
            ),
        ]
        return urlpatterns + urls
    
    def bulk_update_exam_no(self, request):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        if not selected:
            return SimpleTemplateResponse("admin/empty_value_list.html", {"title": "No items selected"})

        # Get the new exam number from the form
        new_exam_no = request.POST.get('new_exam_no')

        # Validate the new exam number
        if not new_exam_no:
            return SimpleTemplateResponse("admin/empty_value_list.html", {"title": "Please enter a new exam number"})

        try:
            new_exam_no = int(new_exam_no)
        except ValueError:
            return SimpleTemplateResponse("admin/empty_value_list.html", {"title": "Invalid exam number"})

        # Check for deletion confirmation
        can_delete = self.has_delete_permission(request)
        if can_delete:
            to_be_deleted = get_deleted_objects(self.model, selected)
            context = {
                'queryset': Student.objects.filter(pk__in=selected),
                'opts': self.model._meta,
                'to_be_deleted': to_be_deleted,
                'new_exam_no': new_exam_no,
            }
            return SimpleTemplateResponse("admin/confirm_bulk_update.html", context)
        else:
            raise PermissionDenied

    @transaction.atomic
    def bulk_update_exam_no_confirmed(self, request, new_exam_no):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        queryset = Student.objects.filter(pk__in=selected)
        queryset.update(examNo=new_exam_no)
        self.message_user(request, f"Updated {queryset.count()} students with new exam number {new_exam_no}.")
        return self.get_changelist_url(request)   


# Register the StudentAdmin class with the Django admin
admin.site.register(Student, StudentAdmin)