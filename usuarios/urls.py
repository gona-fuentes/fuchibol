from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import index, registrar_usuario, perfil

urlpatterns = [
    path('', index, name='index'),  # ruta principal como 'index'
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('registrar/', registrar_usuario, name='registrar'),
    path('dashboard_usuario/', perfil, name='dashboard_usuario'),

    # Cambio de contraseña
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='usuarios/password_change.html', 
            success_url=reverse_lazy('password_change_done')
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='usuarios/password_change_done.html'),
        name='password_change_done'
    ),
]
