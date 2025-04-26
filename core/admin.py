from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from .models import Topic, Quiz, Question, Choice, UserQuizResult
from .models import UserAnswer
admin.site.register(UserAnswer)

# Custom inline formset for validation
class ChoiceInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        correct_count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):  # skip deleted forms
                if form.cleaned_data.get('is_correct'):
                    correct_count += 1

        if correct_count != 1:
            raise ValidationError('Each question must have exactly ONE correct choice.')

# Inline admin for choices
class ChoiceInline(admin.TabularInline):
    model = Choice
    formset = ChoiceInlineFormSet
    extra = 4
    max_num = 4
    min_num = 4
    can_delete = False

# Attach inline to Question admin
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

# Register models
admin.site.register(Topic)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserQuizResult)


