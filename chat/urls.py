from django.urls import path
from .views import MessageListAPIView, AuthenticatedUser, RefreshTokenV, add_comment, logoutView, signUpView

urlpatterns = [
    path('messages/<str:room_name>/', MessageListAPIView.as_view(), name='room-messages'),
    path('api/token/login/', AuthenticatedUser.as_view(), name='token_obtain_pair'),
    path('api/token/logout/', logoutView.as_view(), name='token_logout'),
    path('api/token/refresh/', RefreshTokenV.as_view(), name='token_refresh'),
    path('add-comment/<slug:slug>/', add_comment, name='add_comment'),
    path('signUp/', signUpView.as_view(), name='sign_up')
]
