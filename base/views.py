from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

class CustomLoginView(LoginView):
   template_name = 'base/login.html'
   fields = '__all__'
   #Se já estiver logado não irá para a pag. de login, permanecerá na msm pag. (?)
   redirect_authenticated_user = True 

   def get_success_url(self):
      return reverse_lazy('tasks')

class RegisterPage(FormView):
   template_name = 'base/register.html'
   form_class = UserCreationForm
   #redirect_authenticated_user = True (não tá funcionando, por isso o método get abaixo)
   success_url = reverse_lazy('tasks')

   def form_valid(self, form):
      user = form.save()
      print("user: {} - id: {}".format(user, user.id))
      if user is not None:
         login(self.request, user) #linha 8
      return super(RegisterPage, self).form_valid(form)
   
   #Se o usuário estiver logago, não poderá acessar a página de registro
   def get(self, *args, **kwargs):
      if self.request.user.is_authenticated:
         return redirect('tasks')
      return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
   model = Task
   context_object_name = "tasks"

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['tasks'] = context['tasks'].filter(user=self.request.user)
      context['count'] = context['tasks'].filter(complete=False).count()
      search_input = self.request.GET.get('search-area') or ''
      if search_input:
         context['tasks'] = context['tasks'].filter(title__startswith=search_input) or context['tasks'].filter(title__icontains=search_input)
      
      context['search_input'] = search_input #fazendo assim o campo input 'search-area' ficará escrito com o valor procurado após a busca (em task_list.html)

      return context

class TaskDetail(LoginRequiredMixin, DetailView):
   model = Task
   context_object_name = "task"

class TaskCreate(LoginRequiredMixin,CreateView):
   model = Task
   fields = ['title', 'description', 'complete']
   success_url = reverse_lazy('tasks')

   def form_valid(self, form):
      form.instance.user = self.request.user
      return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
   model = Task
   fields = ['title', 'description', 'complete']
   template_name = 'base/task_update.html'
   success_url = reverse_lazy('tasks')

class TaskDelete(LoginRequiredMixin, DeleteView):
   model = Task
   context_object_name = 'task'
   success_url = reverse_lazy('tasks')