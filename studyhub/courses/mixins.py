from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden


class IsTutorMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является преподавателем"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        user_profile = getattr(self.request.user, 'user_profile', None)
        if not user_profile:
            return False
        return user_profile.is_tutor()
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Доступ запрещен. Только преподаватели могут выполнять это действие.')
            return redirect('home')
        else:
            return redirect('login')


class IsAdminMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является администратором"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        user_profile = getattr(self.request.user, 'user_profile', None)
        if not user_profile:
            return False
        return user_profile.is_admin()
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Доступ запрещен. Только администраторы могут выполнять это действие.')
            return redirect('home')
        else:
            return redirect('login')


class IsTutorOrAdminMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является преподавателем или администратором"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        user_profile = getattr(self.request.user, 'user_profile', None)
        if not user_profile:
            return False
        return user_profile.is_tutor_or_admin()
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Доступ запрещен. Только преподаватели и администраторы могут выполнять это действие.')
            return redirect('home')
        else:
            return redirect('login')


class IsCourseAuthorOrAdminMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является автором курса или администратором"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        # Администратор может все
        user_profile = getattr(self.request.user, 'user_profile', None)
        if user_profile and user_profile.is_admin():
            return True
        
        # Проверяем, является ли пользователь автором курса
        course = self.get_object()
        return self.request.user == course.author
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Доступ запрещен. Вы не являетесь автором этого курса и не являетесь администратором.')
            return redirect('home')
        else:
            return redirect('login')


class IsModuleCourseAuthorOrAdminMixin(UserPassesTestMixin):
    """Миксин для проверки прав на модуль - автор курса или администратор"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        # Администратор может все
        user_profile = getattr(self.request.user, 'user_profile', None)
        if user_profile and user_profile.is_admin():
            return True
        
        # Получаем модуль и проверяем автора курса
        try:
            module = self.get_object()
            return self.request.user == module.course.author
        except:
            # Если get_object не работает, пробуем получить через kwargs
            from .models import Module
            module_pk = self.kwargs.get('module_pk')
            if module_pk:
                module = get_object_or_404(Module, pk=module_pk)
                return self.request.user == module.course.author
            return False
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Доступ запрещен. Вы не являетесь автором этого курса и не являетесь администратором.')
            return redirect('home')
        else:
            return redirect('login')


class IsLessonCourseAuthorOrAdminMixin(UserPassesTestMixin):
    """Миксин для проверки прав на урок - автор курса или администратор"""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        # Администратор может все
        user_profile = getattr(self.request.user, 'user_profile', None)
        if user_profile and user_profile.is_admin():
            return True
        
        # Получаем урок и проверяем автора курса
        lesson = self.get_object()
        return self.request.user == lesson.module.course.author
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Доступ запрещен. Вы не являетесь автором этого курса и не являетесь администратором.')
            return redirect('home')
        else:
            return redirect('login')

