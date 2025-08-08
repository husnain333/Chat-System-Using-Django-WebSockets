from django.shortcuts import render
from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .authentication import CookieJWTAuthentication
from django import forms
from django.http import HttpResponseRedirect
from chat import tasks
from .models import Comment
from .models import User
from .tasks import confirmationEmail
class MessageListAPIView(generics.ListAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        room_name = self.kwargs['room_name']
        return Message.objects.filter(room__name=room_name).order_by('timestamp')

class AuthenticatedUser(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access_token = response.data['access']
        refresh_token = response.data['refresh']

        res = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        res.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
        res.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax')
        return res

class signUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(email=serializer.validated_data['email']).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            confirmationEmail.delay(email, username)
            return Response({"message": "User created successfully and confirmation email will be sent"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class logoutView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:
            return Response({'detail': 'Refresh token missing in cookies'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        except Exception as e:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenV(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "Refresh token not found in cookies."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)
        access_token = serializer.validated_data["access"]
        res = Response({"access": access_token}, status=status.HTTP_200_OK)
        res.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
        return res




class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email_address', 'homepage', 'comment']

def add_comment(request, slug, template_name='comments/create.html'):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save()
            tasks.spam_filter.delay(comment.id, request.META.get('REMOTE_ADDR'))
            return HttpResponseRedirect('/')
    else:
        form = CommentForm()
    
    return render(request, template_name, {'form': form})


        