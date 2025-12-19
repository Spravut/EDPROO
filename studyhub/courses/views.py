from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView, DeleteView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django import forms
from .mixins import (
    IsTutorOrAdminMixin, 
    IsCourseAuthorOrAdminMixin,
    IsModuleCourseAuthorOrAdminMixin,
    IsLessonCourseAuthorOrAdminMixin,
    IsAdminMixin
)
from .models import (
    Course,
    Category,
    Review,
    Enrollment,
    UserProfile,
    Module,
    Lesson,
    Progress,
    Order,
    OrderItem,
    SupportRequest,
)
from .forms import (
    UserRegisterForm,
    ContactForm,
    ReviewForm,
    EnrollmentForm,
    ProfileForm,
    ModuleForm,
    LessonForm,
)

class HomePageView(TemplateView):
    template_name = 'courses/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_published = Course.objects.filter(is_published=True)
        featured = all_published.filter(is_popular=True)[:3]
        if not featured:
            featured = all_published[:3]
        context['featured_courses'] = featured
        context['free_courses'] = all_published.filter(is_free=True)[:3]
        context['total_courses'] = all_published.count()
        return context

class AboutPageView(TemplateView):
    template_name = 'courses/about.html'

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)
        
        category_id = self.request.GET.get('category')
        if category_id and category_id != 'all':
            queryset = queryset.filter(category_id=category_id)

        level = self.request.GET.get('level')
        if level and level != 'all':
            queryset = queryset.filter(level=level)

        show_free_only = self.request.GET.get('free') == 'on'
        if show_free_only:
            queryset = queryset.filter(is_free=True)

        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(author__username__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category', 'all')
        context['search_query'] = self.request.GET.get('search', '')
        context['current_level'] = self.request.GET.get('level', 'all')
        context['free_only'] = self.request.GET.get('free') == 'on'
        context['levels'] = Course.LEVEL_CHOICES
        
        categories_with_counts = []
        for category in context['categories']:
            count = Course.objects.filter(
                category=category,
                is_published=True
            ).count()
            categories_with_counts.append({
                'category': category,
                'count': count
            })
        context['categories_with_counts'] = categories_with_counts
        
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        # Получаем все отзывы для курса
        reviews = Review.objects.filter(course=course).select_related('user').order_by('-created_at')
        context['reviews'] = reviews
        
        # Статистика отзывов
        review_count = reviews.count()
        context['review_count'] = review_count
        
        if review_count > 0:
            avg_rating = sum(review.rating for review in reviews) / review_count
            context['average_rating'] = round(avg_rating, 1)
        else:
            context['average_rating'] = None
        
        # Проверяем, оставлял ли текущий пользователь отзыв
        if self.request.user.is_authenticated:
            context['has_reviewed'] = Review.objects.filter(
                course=course,
                user=self.request.user
            ).exists()
        else:
            context['has_reviewed'] = False
        
        # Проверяем, записан ли пользователь на курс
        if self.request.user.is_authenticated:
            try:
                enrollment = Enrollment.objects.get(
                    user=self.request.user,
                    course=course
                )
                context['user_enrolled'] = True
                context['enrollment_date'] = enrollment.enrolled_at
                context['enrollment_completed'] = enrollment.completed
            except Enrollment.DoesNotExist:
                context['user_enrolled'] = False
        else:
            context['user_enrolled'] = False
        
        # Похожие курсы
        similar_courses = Course.objects.filter(
            category=course.category,
            is_published=True
        ).exclude(pk=course.pk)[:3]
        context['similar_courses'] = similar_courses
        
        # Добавляем данные о прогрессе (ОБНОВЛЕННЫЙ КОД)
        if self.request.user.is_authenticated and hasattr(self.request.user, 'enrollment_set'):
            if self.request.user.enrollment_set.filter(course=course).exists():
                # Прогресс курса
                completed_lessons = Progress.objects.filter(
                    user=self.request.user,
                    lesson__module__course=course,
                    completed=True
                ).count()
                total_lessons = Lesson.objects.filter(module__course=course).count()
                progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
                
                context['user_progress'] = {
                    'completed_lessons': completed_lessons,
                    'total_lessons': total_lessons,
                    'percentage': progress_percentage,
                    'has_progress': completed_lessons > 0
                }
        
        return context

class CourseCreateView(LoginRequiredMixin, IsTutorOrAdminMixin, CreateView):
    """Создание курса - только для преподавателей и администраторов"""
    model = Course
    template_name = 'courses/course_form.html'
    fields = ['title', 'description', 'category', 'level', 'price', 'duration_hours', 'is_published']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Курс успешно создан!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.pk})

class CourseUpdateView(LoginRequiredMixin, IsCourseAuthorOrAdminMixin, UpdateView):
    """Редактирование курса - только автор или администратор"""
    model = Course
    template_name = 'courses/course_form.html'
    fields = ['title', 'description', 'category', 'level', 'price', 'duration_hours', 'is_published']
    
    def form_valid(self, form):
        messages.success(self.request, 'Курс успешно обновлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.pk})

class CourseDeleteView(LoginRequiredMixin, IsCourseAuthorOrAdminMixin, DeleteView):
    """Удаление курса - только автор или администратор"""
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Курс успешно удален!')
        return reverse_lazy('course_list')

class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/register.html'
    success_url = '/'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        
        # Профиль уже создан в методе save формы с выбранной ролью
        
        login(self.request, user)
        role_display = user.user_profile.get_role_display() if hasattr(user, 'user_profile') else 'пользователь'
        messages.success(
            self.request, 
            f'Добро пожаловать, {user.username}! Вы зарегистрированы как {role_display}. Регистрация прошла успешно.'
        )
        return response

class MyCoursesView(LoginRequiredMixin, ListView):
    template_name = 'courses/my_courses.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        user_profile = getattr(self.request.user, 'user_profile', None)
        
        # Для студентов - только курсы, на которые они записались
        if user_profile and user_profile.is_student():
            enrollments = Enrollment.objects.filter(user=self.request.user).select_related('course')
            return [enrollment.course for enrollment in enrollments]
        
        # Для преподавателей и администраторов - курсы, на которые записались + созданные курсы
        elif user_profile and user_profile.is_tutor_or_admin():
            # Курсы, на которые записались (через Enrollment)
            enrollment_ids = Enrollment.objects.filter(user=self.request.user).values_list('course_id', flat=True)
            enrolled_courses = Course.objects.filter(id__in=enrollment_ids)
            
            # Курсы, которые создали
            created_courses = Course.objects.filter(author=self.request.user)
            
            # Объединяем и убираем дубликаты
            all_courses = (enrolled_courses | created_courses).distinct()
            return all_courses
        
        # Если профиля нет, возвращаем пустой список
        return Course.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = getattr(self.request.user, 'user_profile', None)
        
        from django.db.models import Sum
        
        # Для студентов
        if user_profile and user_profile.is_student():
            # Получаем курсы через Enrollment
            enrollment_ids = Enrollment.objects.filter(user=self.request.user).values_list('course_id', flat=True)
            enrolled_courses = Course.objects.filter(id__in=enrollment_ids)
            
            context['enrolled_courses'] = enrolled_courses
            context['enrolled_count'] = enrolled_courses.count()
            context['total_hours'] = enrolled_courses.aggregate(total=Sum('duration_hours'))['total'] or 0
            
            # Статистика для студентов
            context['is_student'] = True
            context['is_tutor'] = False
            
        # Для преподавателей и администраторов
        elif user_profile and user_profile.is_tutor_or_admin():
            # Курсы, на которые записались (через Enrollment)
            enrollment_ids = Enrollment.objects.filter(user=self.request.user).values_list('course_id', flat=True)
            enrolled_courses = Course.objects.filter(id__in=enrollment_ids)
            
            # Курсы, которые создали
            created_courses = Course.objects.filter(author=self.request.user)
            
            context['enrolled_courses'] = enrolled_courses
            context['created_courses'] = created_courses
            
            # Статистика по записанным курсам
            context['enrolled_count'] = enrolled_courses.count()
            context['enrolled_hours'] = enrolled_courses.aggregate(total=Sum('duration_hours'))['total'] or 0
            
            # Статистика по созданным курсам
            context['created_count'] = created_courses.count()
            context['published_count'] = created_courses.filter(is_published=True).count()
            context['draft_count'] = created_courses.filter(is_published=False).count()
            context['created_hours'] = created_courses.aggregate(total=Sum('duration_hours'))['total'] or 0
            
            if context['created_count'] > 0:
                context['published_percent'] = int(
                    (context['published_count'] / context['created_count']) * 100
                )
                context['draft_percent'] = 100 - context['published_percent']
            else:
                context['published_percent'] = 0
                context['draft_percent'] = 0
            
            context['latest_created_course'] = created_courses.order_by('-created_at').first()
            
            context['is_student'] = False
            context['is_tutor'] = True
        
        return context

class ContactFormView(FormView):
    template_name = 'courses/contact_form.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact_form')
    
    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']
        contact_type = form.cleaned_data['contact_type']
        
        # Сохраняем обращение в базу данных
        SupportRequest.objects.create(
            name=name,
            contact=email,
            message=message,
            contact_type=contact_type,
            status='pending'
        )
        
        messages.success(
            self.request, 
            f'Спасибо за ваше обращение, {name}! Мы ответим вам в течение 24 часов.'
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Пожалуйста, исправьте ошибки в форме.'
        )
        return super().form_invalid(form)

class AddReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'courses/add_review.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['pk']
        context['course'] = get_object_or_404(Course, pk=course_id)
        return context
    
    def form_valid(self, form):
        course_id = self.kwargs['pk']
        course = get_object_or_404(Course, pk=course_id)
        
        if Review.objects.filter(course=course, user=self.request.user).exists():
            messages.error(
                self.request,
                'Вы уже оставляли отзыв на этот курс.'
            )
            return redirect('course_detail', pk=course_id)
        
        form.instance.course = course
        form.instance.user = self.request.user
        
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            'Спасибо за ваш отзыв! Он поможет другим студентам.'
        )
        
        return response
    
    def get_success_url(self):
        course_id = self.kwargs['pk']
        return reverse_lazy('course_detail', kwargs={'pk': course_id})

class EnrollView(LoginRequiredMixin, CreateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'courses/enroll_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        course = form.instance.course
        messages.success(
            self.request,
            f'Вы успешно записались на курс "{course.title}"!'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.course.pk})

@login_required
def quick_enroll(request, pk):
    """Прямое зачисление на бесплатный курс (без корзины)"""
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=pk, is_published=True)
        
        # Проверяем, что курс бесплатный
        if not course.is_free:
            messages.error(request, 'Этот курс платный. Добавьте его в корзину для покупки.')
            return redirect('course_detail', pk=pk)
        
        # Проверяем, не записан ли уже пользователь
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            messages.warning(request, 'Вы уже записаны на этот курс!')
        else:
            Enrollment.objects.create(user=request.user, course=course)
            messages.success(request, f'Вы успешно записались на курс "{course.title}"!')
    
    return redirect('course_detail', pk=pk)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = 'courses/profile_update.html'
    success_url = reverse_lazy('my_courses')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'bio': '',
                'phone': '',
                'birth_date': None,
                'avatar': None
            }
        )
        if created:
            messages.info(self.request, 'Создан новый профиль для вас!')
        return profile
    
    def form_valid(self, form):
        # Сохраняем роль из текущего профиля, чтобы она не изменилась
        form.instance.role = self.object.role
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['age'] = self.object.age
        context['is_adult'] = self.object.is_adult()
        # Роль не передается в контекст, так как она не может быть изменена
        return context

class CourseSearchView(ListView):
    model = Course
    template_name = 'courses/course_search.html'
    context_object_name = 'courses'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)
        
        query = self.request.GET.get('q', '').strip()
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(author__username__icontains=query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        context['search_query'] = query
        context['search_count'] = self.get_queryset().count()
        return context

class ModuleListView(ListView):
    template_name = 'courses/module_list.html'
    context_object_name = 'modules'
    
    def get_queryset(self):
        course_pk = self.kwargs['course_pk']
        return Module.objects.filter(course_id=course_pk).order_by('order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_pk = self.kwargs['course_pk']
        course = get_object_or_404(Course, pk=course_pk)
        context['course'] = course
        
        # Рассчитываем общую статистику
        modules = self.get_queryset()
        total_lessons = sum(module.lessons.count() for module in modules)
        total_duration = sum(module.total_duration() for module in modules)
        
        context['total_lessons'] = total_lessons
        context['total_duration'] = total_duration
        
        return context

class ModuleDetailView(DetailView):
    model = Module
    template_name = 'courses/module_detail.html'
    context_object_name = 'module'
    
    def get_object(self, queryset=None):
        course_pk = self.kwargs['course_pk']
        module_pk = self.kwargs['module_pk']
        
        return get_object_or_404(
            Module, 
            pk=module_pk, 
            course_id=course_pk
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = self.object
        
        # Получаем уроки модуля
        lessons = module.lessons.all().order_by('order')
        context['lessons'] = lessons
        
        # Рассчитываем общую продолжительность
        total_duration = sum(lesson.duration_minutes for lesson in lessons)
        context['total_duration'] = total_duration
        
        # Добавляем информацию о прогрессе
        if self.request.user.is_authenticated:
            # Проверяем, записан ли пользователь на курс
            is_enrolled = hasattr(self.request.user, 'enrollment_set') and \
                         self.request.user.enrollment_set.filter(course=module.course).exists()
            
            if is_enrolled:
                # Прогресс модуля
                completed_lessons = Progress.objects.filter(
                    user=self.request.user,
                    lesson__module=module,
                    completed=True
                ).count()
                total_lessons = lessons.count()
                progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
                
                context['user_progress'] = {
                    'completed_lessons': completed_lessons,
                    'total_lessons': total_lessons,
                    'percentage': progress_percentage
                }
                
                # Информация о прогрессе для каждого урока
                lessons_with_progress = []
                for lesson in lessons:
                    progress = Progress.objects.filter(
                        user=self.request.user,
                        lesson=lesson
                    ).first()
                    lessons_with_progress.append({
                        'lesson': lesson,
                        'completed': progress.completed if progress else False,
                        'completed_at': progress.completed_at if progress else None
                    })
                context['lessons_with_progress'] = lessons_with_progress
        
        return context

class LessonDetailView(DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'
    
    def get_object(self, queryset=None):
        course_pk = self.kwargs['course_pk']
        module_pk = self.kwargs['module_pk']
        lesson_pk = self.kwargs['lesson_pk']
        
        return get_object_or_404(
            Lesson.objects.select_related('module__course'),
            pk=lesson_pk,
            module_id=module_pk,
            module__course_id=course_pk
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        
        # Информация для навигации
        context['course'] = lesson.module.course
        context['module'] = lesson.module
        
        # Находим предыдущий и следующий уроки
        lessons = list(lesson.module.lessons.all().order_by('order'))
        current_index = lessons.index(lesson)
        
        if current_index > 0:
            context['previous_lesson'] = lessons[current_index - 1]
        
        if current_index < len(lessons) - 1:
            context['next_lesson'] = lessons[current_index + 1]
        
        # Добавляем информацию о прогрессе
        if self.request.user.is_authenticated:
            # Проверяем, записан ли пользователь на курс
            is_enrolled = hasattr(self.request.user, 'enrollment_set') and \
                         self.request.user.enrollment_set.filter(course=lesson.module.course).exists()
            
            if is_enrolled:
                # Прогресс текущего урока
                progress = Progress.objects.filter(
                    user=self.request.user,
                    lesson=lesson
                ).first()
                
                context['user_progress'] = {
                    'completed': progress.completed if progress else False,
                    'completed_at': progress.completed_at if progress else None
                }
                
                # Прогресс модуля
                module = lesson.module
                module_completed = Progress.objects.filter(
                    user=self.request.user,
                    lesson__module=module,
                    completed=True
                ).count()
                module_total = module.lessons.count()
                module_progress = int((module_completed / module_total) * 100) if module_total > 0 else 0
                
                context['module_progress'] = {
                    'completed': module_completed,
                    'total': module_total,
                    'percentage': module_progress
                }
                
                # Прогресс курса
                course = lesson.module.course
                course_completed = Progress.objects.filter(
                    user=self.request.user,
                    lesson__module__course=course,
                    completed=True
                ).count()
                course_total = Lesson.objects.filter(module__course=course).count()
                course_progress = int((course_completed / course_total) * 100) if course_total > 0 else 0
                
                context['course_progress'] = {
                    'completed': course_completed,
                    'total': course_total,
                    'percentage': course_progress
                }
        
        return context

class ModuleCreateView(LoginRequiredMixin, IsTutorOrAdminMixin, CreateView):
    """Создание модуля - только преподаватели и администраторы"""
    model = Module
    form_class = ModuleForm
    template_name = 'courses/module_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Дополнительная проверка: пользователь должен быть автором курса или администратором
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        user_profile = getattr(request.user, 'user_profile', None)
        if not (user_profile and user_profile.is_admin()) and request.user != course.author:
            messages.error(request, 'Вы можете создавать модули только для своих курсов.')
            return redirect('course_detail', pk=course.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        form.instance.course = course
        messages.success(self.request, 'Модуль успешно создан!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('module_list', kwargs={'course_pk': self.kwargs['course_pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        context['course'] = course  # <-- ВАЖНО: добавляем курс в контекст
        return context

class LessonCreateView(LoginRequiredMixin, IsTutorOrAdminMixin, CreateView):
    """Создание урока - только преподаватели и администраторы"""
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Дополнительная проверка: пользователь должен быть автором курса или администратором
        module = get_object_or_404(Module, pk=self.kwargs['module_pk'])
        user_profile = getattr(request.user, 'user_profile', None)
        if not (user_profile and user_profile.is_admin()) and request.user != module.course.author:
            messages.error(request, 'Вы можете создавать уроки только для своих курсов.')
            return redirect('module_detail', course_pk=module.course.pk, module_pk=module.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        module = get_object_or_404(Module, pk=self.kwargs['module_pk'])
        form.instance.module = module
        messages.success(self.request, 'Урок успешно создан!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy(
            'module_detail',
            kwargs={
                'course_pk': self.kwargs['course_pk'],
                'module_pk': self.kwargs['module_pk']
            }
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = get_object_or_404(Module, pk=self.kwargs['module_pk'])
        context['module'] = module  # <-- ВАЖНО
        context['course'] = module.course  # <-- ВАЖНО
        return context

class ModuleUpdateView(LoginRequiredMixin, IsModuleCourseAuthorOrAdminMixin, UpdateView):
    """Редактирование модуля - только автор курса или администратор"""
    model = Module
    form_class = ModuleForm
    template_name = 'courses/module_form.html'
    
    def get_object(self, queryset=None):
        module_pk = self.kwargs['module_pk']
        course_pk = self.kwargs['course_pk']
        return get_object_or_404(Module, pk=module_pk, course_id=course_pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = self.object
        context['course'] = module.course  # <-- ВАЖНО: добавляем курс в контекст
        return context
    
    def get_success_url(self):
        return reverse_lazy('module_detail', kwargs={
            'course_pk': self.object.course.pk,
            'module_pk': self.object.pk
        })

class ModuleDeleteView(LoginRequiredMixin, IsModuleCourseAuthorOrAdminMixin, DeleteView):
    """Удаление модуля - только автор курса или администратор"""
    model = Module
    template_name = 'courses/module_confirm_delete.html'
    
    def get_object(self, queryset=None):
        module_pk = self.kwargs['module_pk']
        course_pk = self.kwargs['course_pk']
        return get_object_or_404(Module, pk=module_pk, course_id=course_pk)
    
    def get_success_url(self):
        messages.success(self.request, 'Модуль успешно удален!')
        return reverse_lazy('module_list', kwargs={'course_pk': self.object.course.pk})

class LessonUpdateView(LoginRequiredMixin, IsLessonCourseAuthorOrAdminMixin, UpdateView):
    """Редактирование урока - только автор курса или администратор"""
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'
    
    def get_object(self, queryset=None):
        lesson_pk = self.kwargs['pk']
        module_pk = self.kwargs['module_pk']
        course_pk = self.kwargs['course_pk']
        
        return get_object_or_404(
            Lesson,
            pk=lesson_pk,
            module_id=module_pk,
            module__course_id=course_pk
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        context['course'] = lesson.module.course  # <-- ВАЖНО
        context['module'] = lesson.module  # <-- ВАЖНО
        return context
    
    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs={
            'course_pk': self.object.module.course.pk,
            'module_pk': self.object.module.pk,
            'lesson_pk': self.object.pk
        })


class TutorsListView(TemplateView):
    """Список преподавателей (пользователи с ролью 'tutor')"""
    template_name = 'courses/tutors.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tutors'] = UserProfile.objects.filter(role='tutor').select_related('user')
        return context


class CartView(TemplateView):
    """Страница корзины с выбранными курсами"""
    template_name = 'courses/cart.html'

    def get_cart_course_ids(self):
        return self.request.session.get('cart', [])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_ids = self.get_cart_course_ids()
        all_courses = Course.objects.filter(id__in=cart_ids, is_published=True)
        
        # Фильтруем бесплатные курсы из корзины (они не должны там быть)
        free_courses = [c for c in all_courses if c.is_free]
        paid_courses = [c for c in all_courses if not c.is_free]
        
        # Удаляем бесплатные курсы из корзины
        if free_courses:
            cart_ids = [c.id for c in paid_courses]
            self.request.session['cart'] = cart_ids
            for course in free_courses:
                messages.warning(
                    self.request,
                    f'Курс "{course.title}" бесплатный и был удален из корзины. Используйте кнопку "Записаться сразу" на странице курса.'
                )
        
        total_amount = sum(course.price for course in paid_courses)
        context['courses'] = paid_courses
        context['total_amount'] = total_amount
        return context


class AddToCartView(LoginRequiredMixin, View):
    """Добавление платного курса в корзину"""

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=kwargs['pk'], is_published=True)
        
        # Проверяем, что курс платный
        if course.is_free:
            messages.error(request, 'Бесплатные курсы нельзя добавлять в корзину. Используйте кнопку "Записаться сразу".')
            return redirect('course_detail', pk=course.pk)
        
        # Проверяем, не записан ли уже пользователь
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            messages.warning(request, 'Вы уже записаны на этот курс!')
            return redirect('course_detail', pk=course.pk)
        
        cart = request.session.get('cart', [])
        if course.id not in cart:
            cart.append(course.id)
            request.session['cart'] = cart
            messages.success(request, f'Курс «{course.title}» добавлен в корзину.')
        else:
            messages.info(request, 'Этот курс уже есть в вашей корзине.')
        return redirect('cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    """Удаление курса из корзины"""

    def post(self, request, *args, **kwargs):
        cart = request.session.get('cart', [])
        course_id = kwargs['pk']
        if course_id in cart:
            cart.remove(course_id)
            request.session['cart'] = cart
            messages.success(request, 'Курс удалён из корзины.')
        return redirect('cart')


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Оформление заказа из корзины"""
    template_name = 'courses/checkout.html'

    def get_cart_courses(self):
        cart_ids = self.request.session.get('cart', [])
        return Course.objects.filter(id__in=cart_ids, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = self.get_cart_courses()
        # В корзине должны быть только платные курсы
        paid_courses = [c for c in courses if not c.is_free]
        total_amount = sum(course.price for course in paid_courses)
        context['courses'] = paid_courses
        context['total_amount'] = total_amount
        return context

    def post(self, request, *args, **kwargs):
        courses = self.get_cart_courses()
        if not courses:
            messages.warning(request, 'Ваша корзина пуста.')
            return redirect('cart')

        # Фильтруем только платные курсы (бесплатные не должны быть в корзине)
        paid_courses = [c for c in courses if not c.is_free]
        
        if not paid_courses:
            messages.warning(request, 'В корзине нет платных курсов для оплаты.')
            return redirect('cart')

        # Создаём заказ только для платных курсов
        order = Order.objects.create(user=request.user, status='paid')
        for course in paid_courses:
            OrderItem.objects.create(
                order=order,
                course=course,
                price=course.price
            )
            # После оплаты создаём Enrollment - доступ к курсу
            Enrollment.objects.get_or_create(user=request.user, course=course)

        # Очищаем корзину
        request.session['cart'] = []

        messages.success(request, f'Заказ #{order.pk} успешно оформлен. Доступ к курсам выдан.')
        return redirect('orders_history')


class OrdersHistoryView(LoginRequiredMixin, ListView):
    """История заказов пользователя"""
    model = Order
    template_name = 'courses/orders_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__course')


class AssistantFAQView(TemplateView):
    """Простой онлайн‑ассистент на основе категорий вопросов"""
    template_name = 'courses/assistant_faq.html'

    # Данные FAQ хранятся в коде
    FAQ_DATA = [
        {
            'id': 1,
            'name': 'Общие вопросы',
            'questions': [
                {
                    'id': 1,
                    'question': 'Что такое EdPro?',
                    'answer': 'EdPro — это онлайн‑платформа для развития навыков, где практикующие преподаватели создают и ведут курсы по различным направлениям. Мы предлагаем качественное образование в удобном формате.'
                },
                {
                    'id': 2,
                    'question': 'Как начать обучение?',
                    'answer': 'Для начала обучения вам нужно зарегистрироваться на платформе, выбрать интересующий курс и, если курс платный, оплатить его. После этого вы получите доступ ко всем материалам курса.'
                },
                {
                    'id': 3,
                    'question': 'Нужна ли регистрация для просмотра курсов?',
                    'answer': 'Да, для прохождения курсов необходима регистрация на платформе. Это позволяет нам сохранять ваш прогресс и предоставлять персонализированный опыт обучения.'
                },
                {
                    'id': 4,
                    'question': 'Можно ли проходить курсы на мобильных устройствах?',
                    'answer': 'Да, наша платформа адаптирована для работы на различных устройствах, включая смартфоны и планшеты. Вы можете учиться в любое время и в любом месте.'
                }
            ]
        },
        {
            'id': 2,
            'name': 'Оплата и возврат',
            'questions': [
                {
                    'id': 5,
                    'question': 'Какие способы оплаты доступны?',
                    'answer': 'Мы принимаем оплату банковскими картами (Visa, MasterCard, МИР), а также другие популярные способы оплаты. Все платежи обрабатываются через защищенные платежные системы.'
                },
                {
                    'id': 6,
                    'question': 'Можно ли вернуть деньги за курс?',
                    'answer': 'Да, мы предоставляем гарантию возврата средств в течение 14 дней с момента покупки курса, если вы не начали его прохождение. Для возврата средств обратитесь в службу поддержки.'
                },
                {
                    'id': 7,
                    'question': 'Что делать, если оплата не прошла?',
                    'answer': 'Если оплата не прошла, проверьте правильность данных карты и наличие средств. Если проблема сохраняется, обратитесь в службу поддержки или попробуйте другой способ оплаты.'
                },
                {
                    'id': 8,
                    'question': 'Есть ли бесплатные курсы?',
                    'answer': 'Да, на платформе есть бесплатные курсы. Вы можете найти их, используя фильтр "Только бесплатные" на странице со списком курсов.'
                }
            ]
        },
        {
            'id': 3,
            'name': 'Техническая поддержка',
            'questions': [
                {
                    'id': 9,
                    'question': 'Не могу войти в свой аккаунт',
                    'answer': 'Если вы не можете войти в аккаунт, проверьте правильность ввода логина и пароля. Если проблема сохраняется, воспользуйтесь функцией восстановления пароля или обратитесь в службу поддержки.'
                },
                {
                    'id': 10,
                    'question': 'Видео не загружается или тормозит',
                    'answer': 'Проблемы с загрузкой видео могут быть связаны с медленным интернет‑соединением. Попробуйте снизить качество видео, обновить страницу или проверить скорость интернета. Если проблема не решается, обратитесь в поддержку.'
                },
                {
                    'id': 11,
                    'question': 'Как восстановить доступ к курсу?',
                    'answer': 'Если вы потеряли доступ к курсу, убедитесь, что вы вошли в правильный аккаунт. Все купленные курсы сохраняются в разделе "Мои курсы". Если курс не отображается, обратитесь в службу поддержки.'
                },
                {
                    'id': 12,
                    'question': 'Какие браузеры поддерживаются?',
                    'answer': 'Платформа работает во всех современных браузерах: Chrome, Firefox, Safari, Edge. Рекомендуем использовать последние версии браузеров для лучшей производительности.'
                }
            ]
        },
        {
            'id': 4,
            'name': 'О курсах',
            'questions': [
                {
                    'id': 13,
                    'question': 'Как долго длится курс?',
                    'answer': 'Длительность курсов варьируется в зависимости от программы. Каждый курс имеет указанное количество часов обучения. Вы можете проходить курс в своем темпе, без ограничений по времени.'
                },
                {
                    'id': 14,
                    'question': 'Получу ли я сертификат после прохождения курса?',
                    'answer': 'Да, после успешного прохождения курса и выполнения всех заданий вы получите сертификат, который можно скачать в разделе "Мои курсы".'
                },
                {
                    'id': 15,
                    'question': 'Можно ли скачать материалы курса?',
                    'answer': 'Да, многие материалы курса доступны для скачивания. Это зависит от конкретного курса и решений преподавателя. Обычно презентации, документы и дополнительные материалы можно скачать.'
                },
                {
                    'id': 16,
                    'question': 'Как связаться с преподавателем?',
                    'answer': 'Вы можете задать вопросы преподавателю через систему сообщений на платформе или оставить комментарий к уроку. Преподаватели обычно отвечают в течение 24-48 часов.'
                },
                {
                    'id': 17,
                    'question': 'Что делать, если курс не подошел?',
                    'answer': 'Если курс не соответствует вашим ожиданиям, вы можете обратиться в службу поддержки в течение 14 дней с момента покупки для возврата средств. Мы также рекомендуем внимательно изучать описание курса перед покупкой.'
                }
            ]
        }
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем категории из кода
        categories = self.FAQ_DATA
        current_category_id = self.request.GET.get('category')
        current_category = None
        questions = []

        # Находим выбранную категорию
        if current_category_id:
            try:
                category_id = int(current_category_id)
                current_category = next((cat for cat in categories if cat['id'] == category_id), None)
            except (ValueError, TypeError):
                pass
        
        # Если категория не выбрана, берем первую
        if not current_category and categories:
            current_category = categories[0]

        # Получаем вопросы выбранной категории
        if current_category:
            questions = current_category.get('questions', [])

        context['categories'] = categories
        context['current_category'] = current_category
        context['questions'] = questions
        return context


class AssistantContactView(FormView):
    """Форма 'не нашли ответ — оставьте контакт'"""
    template_name = 'courses/assistant_contact.html'
    success_url = reverse_lazy('assistant_contact')

    class SimpleSupportForm(forms.Form):
        name = forms.CharField(label='Ваше имя', max_length=100)
        contact = forms.CharField(
            label='Контакт для связи (email, Telegram и т.п.)',
            max_length=150,
        )
        message = forms.CharField(
            label='Ваш вопрос',
            widget=forms.Textarea(attrs={'rows': 4}),
        )

    form_class = SimpleSupportForm

    def form_valid(self, form):
        SupportRequest.objects.create(
            name=form.cleaned_data['name'],
            contact=form.cleaned_data['contact'],
            message=form.cleaned_data['message'],
            status='pending'
        )
        messages.success(
            self.request,
            'Спасибо! Мы получили ваш вопрос и свяжемся с вами по указанному контакту.',
        )
        return super().form_valid(form)


class AdminStatsView(UserPassesTestMixin, TemplateView):
    """Простая страница аналитики (для администратора)"""
    template_name = 'courses/admin_stats.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Топ‑5 самых продаваемых курсов
        top_courses = (
            OrderItem.objects.values('course__title')
            .annotate(total_sold=Sum('id'))
            .order_by('-total_sold')[:5]
        )

        # Выручка за последний месяц по оплаченным заказам
        last_month = timezone.now() - timezone.timedelta(days=30)
        recent_paid_items = OrderItem.objects.filter(
            order__status='paid',
            order__created_at__gte=last_month,
        )
        revenue_last_month = recent_paid_items.aggregate(total=Sum('price'))['total'] or 0
        orders_count_last_month = (
            Order.objects.filter(status='paid', created_at__gte=last_month).count()
        )

        context['top_courses'] = top_courses
        context['revenue_last_month'] = revenue_last_month
        context['orders_count_last_month'] = orders_count_last_month
        return context


class CourseRecommendationView(FormView):
    """Улучшенный подбор курсов на основе детальных вопросов"""
    template_name = 'courses/recommendation_test.html'
    form_class = None  # Будет установлен в get_form_class
    
    def get_form_class(self):
        from .forms import CourseRecommendationForm
        return CourseRecommendationForm
    
    def get_initial(self):
        """Устанавливаем начальные значения для формы"""
        initial = super().get_initial()
        # Если форма уже была отправлена, используем GET параметры
        if self.request.method == 'GET' and self.request.GET:
            for key in self.request.GET:
                if key in ['coding_interest', 'design_interest', 'web_development', 
                          'mobile_development', 'database_interest', 'ml_interest',
                          'team_work', 'learning_format', 'study_time', 
                          'theory_practice', 'level']:
                    initial[key] = self.request.GET.get(key)
                elif key == 'free_only':
                    initial[key] = self.request.GET.get(key) == 'on'
        return initial
    
    def get(self, request, *args, **kwargs):
        """Обработка GET запроса - показываем форму и результаты если есть"""
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result_courses'] = None
        context['recommendation_score'] = None
        
        # Обрабатываем результаты формы
        if self.request.method == 'GET' and self.request.GET.get('coding_interest'):
            result_courses = self._get_recommended_courses()
            context['result_courses'] = result_courses
            context['recommendation_score'] = self._calculate_scores()
        
        return context
    
    def _calculate_scores(self):
        """Вычисляет баллы интересов пользователя на основе ответов"""
        scores = {
            'programming': int(self.request.GET.get('coding_interest', 3)),
            'design': int(self.request.GET.get('design_interest', 3)),
            'web': int(self.request.GET.get('web_development', 3)),
            'mobile': int(self.request.GET.get('mobile_development', 3)),
            'database': int(self.request.GET.get('database_interest', 3)),
            'ml': int(self.request.GET.get('ml_interest', 3)),
        }
        return scores
    
    def _get_recommended_courses(self):
        """Подбирает курсы на основе ответов пользователя"""
        from django.db.models import Q, F, Case, When, IntegerField, Sum
        
        # Получаем ответы
        coding_interest = int(self.request.GET.get('coding_interest', 3))
        design_interest = int(self.request.GET.get('design_interest', 3))
        web_interest = int(self.request.GET.get('web_development', 3))
        mobile_interest = int(self.request.GET.get('mobile_development', 3))
        database_interest = int(self.request.GET.get('database_interest', 3))
        ml_interest = int(self.request.GET.get('ml_interest', 3))
        level = self.request.GET.get('level', 'beginner')
        free_only = self.request.GET.get('free_only') == 'on'
        
        # Начинаем с базового запроса
        qs = Course.objects.filter(is_published=True)
        
        # Фильтр по уровню
        if level:
            qs = qs.filter(level=level)
        
        # Фильтр по бесплатности
        if free_only:
            qs = qs.filter(is_free=True)
        
        # Вычисляем релевантность курсов на основе интересов
        # Создаем систему баллов для каждого курса
        course_scores = []
        
        # Ключевые слова для каждой категории
        programming_keywords = ['программирование', 'python', 'java', 'javascript', 'код', 'разработка', 
                                'developer', 'programming', 'алгоритм', 'структура данных', 'git', 'github']
        design_keywords = ['дизайн', 'design', 'ui', 'ux', 'графика', 'рисование', 'figma', 'photoshop', 
                           'иллюстрация', 'веб-дизайн', 'интерфейс']
        web_keywords = ['веб', 'web', 'сайт', 'html', 'css', 'frontend', 'backend', 'django', 'flask', 
                       'react', 'vue', 'angular', 'node', 'express', 'api', 'rest']
        mobile_keywords = ['мобильн', 'mobile', 'android', 'ios', 'react native', 'flutter', 'swift', 
                          'kotlin', 'приложение', 'app']
        database_keywords = ['база данных', 'database', 'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 
                            'nosql', 'orm', 'данные']
        ml_keywords = ['машинное обучение', 'machine learning', 'ml', 'ai', 'искусственный интеллект', 
                      'нейронн', 'tensorflow', 'pytorch', 'deep learning', 'data science', 'анализ данных']
        
        for course in qs:
            score = 0
            
            # Проверяем категорию и название курса
            category_name = course.category.name.lower() if course.category else ''
            title_lower = course.title.lower()
            description_lower = course.description.lower()
            full_text = f"{category_name} {title_lower} {description_lower}"
            
            # Программирование (учитываем все уровни интереса, но с разным весом)
            if coding_interest >= 3:
                matches = sum(1 for word in programming_keywords if word in full_text)
                if matches > 0:
                    score += coding_interest * (2 + matches)  # Больше совпадений = выше балл
            
            # Дизайн
            if design_interest >= 3:
                matches = sum(1 for word in design_keywords if word in full_text)
                if matches > 0:
                    score += design_interest * (2 + matches)
            
            # Веб-разработка
            if web_interest >= 3:
                matches = sum(1 for word in web_keywords if word in full_text)
                if matches > 0:
                    score += web_interest * (2 + matches)
            
            # Мобильная разработка
            if mobile_interest >= 3:
                matches = sum(1 for word in mobile_keywords if word in full_text)
                if matches > 0:
                    score += mobile_interest * (2 + matches)
            
            # Базы данных
            if database_interest >= 3:
                matches = sum(1 for word in database_keywords if word in full_text)
                if matches > 0:
                    score += database_interest * (2 + matches)
            
            # Машинное обучение
            if ml_interest >= 3:
                matches = sum(1 for word in ml_keywords if word in full_text)
                if matches > 0:
                    score += ml_interest * (2 + matches)
            
            # Бонус за популярность курса
            if course.is_popular:
                score += 5
            
            # Если курс не подходит ни под один интерес, но пользователь выбрал уровень - даем базовый балл
            if score == 0:
                score = 1
            
            course_scores.append((course, score))
        
        # Сортируем по баллам (от большего к меньшему)
        course_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Возвращаем топ-10 курсов
        return [course for course, score in course_scores[:10]]
    
    def form_valid(self, form):
        """Обработка валидной формы - редирект с параметрами"""
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        # Собираем все данные формы в GET параметры
        params = {}
        for field_name, field_value in form.cleaned_data.items():
            if field_value:
                params[field_name] = field_value
        
        # Редиректим на ту же страницу с параметрами
        url = reverse('course_recommendation')
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return HttpResponseRedirect(f'{url}?{query_string}')

# ... предыдущий код остается без изменений ...

class MarkLessonCompletedView(LoginRequiredMixin, View):
    """Представление для отметки урока как пройденного/не пройденного"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        lesson_id = request.POST.get('lesson_id')
        completed = request.POST.get('completed') == 'true'
        
        if not lesson_id:
            return JsonResponse({'success': False, 'error': 'Не указан ID урока'}, status=400)
        
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        
        # Проверяем, имеет ли пользователь доступ к уроку
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Требуется авторизация'}, status=403)
        
        # Проверяем, записан ли пользователь на курс
        if not hasattr(request.user, 'enrollment_set') or \
           not request.user.enrollment_set.filter(course=lesson.module.course).exists():
            return JsonResponse({'success': False, 'error': 'Вы не записаны на этот курс'}, status=403)
        
        # Получаем или создаем запись прогресса
        progress, created = Progress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': completed}
        )
        
        # Если запись уже существует, обновляем ее
        if not created:
            progress.completed = completed
            progress.save()
        
        # Получаем статистику прогресса
        module = lesson.module
        course = module.course
        
        # Прогресс модуля
        module_completed = Progress.objects.filter(
            user=request.user,
            lesson__module=module,
            completed=True
        ).count()
        module_total = module.lessons.count()
        module_progress = int((module_completed / module_total) * 100) if module_total > 0 else 0
        
        # Прогресс курса
        course_completed = Progress.objects.filter(
            user=request.user,
            lesson__module__course=course,
            completed=True
        ).count()
        course_total = Lesson.objects.filter(module__course=course).count()
        course_progress = int((course_completed / course_total) * 100) if course_total > 0 else 0
        
        return JsonResponse({
            'success': True,
            'completed': progress.completed,
            'completed_at': progress.completed_at.strftime('%d.%m.%Y %H:%M') if progress.completed_at else None,
            'module_progress': module_progress,
            'course_progress': course_progress,
            'module_completed': module_completed,
            'module_total': module_total,
            'course_completed': course_completed,
            'course_total': course_total,
            'message': 'Урок отмечен как пройденный' if completed else 'Урок отмечен как непройденный'
        })


class SupportRequestsListView(LoginRequiredMixin, IsAdminMixin, ListView):
    """Список обращений для администраторов"""
    model = SupportRequest
    template_name = 'courses/support_requests_list.html'
    context_object_name = 'requests'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SupportRequest.objects.all()
        status_filter = self.request.GET.get('status', 'pending')
        
        if status_filter == 'pending':
            queryset = queryset.filter(status='pending')
        elif status_filter == 'completed':
            queryset = queryset.filter(status='completed')
        # Если 'all', показываем все
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', 'pending')
        context['pending_count'] = SupportRequest.objects.filter(status='pending').count()
        context['completed_count'] = SupportRequest.objects.filter(status='completed').count()
        context['total_count'] = SupportRequest.objects.count()
        return context


class SupportRequestUpdateStatusView(LoginRequiredMixin, IsAdminMixin, View):
    """Изменение статуса обращения"""
    
    def post(self, request, *args, **kwargs):
        request_obj = get_object_or_404(SupportRequest, pk=kwargs['pk'])
        new_status = request.POST.get('status')
        
        if new_status in ['pending', 'completed']:
            request_obj.status = new_status
            if new_status == 'completed':
                request_obj.completed_at = timezone.now()
            else:
                request_obj.completed_at = None
            request_obj.save()
            
            status_display = 'выполнено' if new_status == 'completed' else 'в рассмотрении'
            messages.success(request, f'Статус обращения изменен на "{status_display}".')
        else:
            messages.error(request, 'Неверный статус.')
        
        return redirect('support_requests_list')