
from django.urls import path
from users.views import UserAPIView

urlpatterns = [
    path('list', UserAPIView.list),
    path('search', UserAPIView.search),
    path('details/<str:acct>', UserAPIView.details),
    path('signup', UserAPIView.signup),
    path('signin', UserAPIView.signin),
    path('delete/<str:acct>', UserAPIView.delete),
    path('update/<str:acct>', UserAPIView.update),
    path('update_fn/<str:acct>', UserAPIView.update_fn),
]