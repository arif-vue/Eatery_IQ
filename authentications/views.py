from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import OTP, UserProfile , CustomUser, OnboardingProgress
from .serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    UserProfileSerializer,
    OTPSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    OnboardingProgressSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import random
from rest_framework.views import APIView
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

def error_response(code, message="Error", details=None):
    return Response({
        "error": True,
        "message": message,
        "details": details or {}
    }, status=code)

def generate_otp():
    return str(random.randint(100000, 999999))

User = get_user_model()

def send_otp_email(email, otp):
    """
    Smart OTP email sending:
    - For test emails (@example.com, @test.com): prints to console
    - For real emails: sends via SMTP
    """
    from django.conf import settings
    
    # Check if this is a test email
    test_domains = getattr(settings, 'TEST_EMAIL_DOMAINS', ['example.com', 'test.com', 'testing.com'])
    domain = email.split('@')[-1].lower()
    is_test_email = domain in test_domains
    
    if is_test_email:
        # Print to console for test emails
        print("\n" + "="*60)
        print("TEST EMAIL (Console Output)")
        print("="*60)
        print(f"To: {email}")
        print(f"Subject: Your OTP Code")
        print(f"OTP: {otp}")
        print("Message: Your OTP code for account verification")
        print("="*60)
        print("This is a test email - not sent to real address")
        print("="*60 + "\n")
        return
    
    # Send real email for non-test addresses
    try:
        html_content = render_to_string('otp_email_template.html', {'otp': otp, 'email': email})
        msg = EmailMultiAlternatives(
            subject='Your OTP Code',
            body=f'Your OTP is {otp}',
            from_email='arif.elixir@gmail.com',
            to=[email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        print(f"REAL EMAIL SENT to: {email}")
    except Exception as e:
        print(f"EMAIL FAILED for {email}: {e}")
        # Fallback: print to console if email fails
        print("\n" + "="*60)
        print("EMAIL FALLBACK (Console Output)")
        print("="*60)
        print(f"To: {email}")
        print(f"Subject: Your OTP Code")
        print(f"OTP: {otp}")
        print("Message: Your OTP code for account verification")
        print("="*60)
        print("Email failed - showing OTP in console")
        print("="*60 + "\n")

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    User Registration
    Required fields: full_name, business_name, role, email, password, confirm_password
    """
    serializer = CustomUserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Send OTP for verification
        otp = generate_otp()
        otp_data = {'email': user.email, 'otp': otp}
        otp_serializer = OTPSerializer(data=otp_data)
        if otp_serializer.is_valid():
            otp_serializer.save()
            try:
                send_otp_email(email=user.email, otp=otp)
            except Exception as e:
                return error_response(
                    code=500,
                    message="Failed to send OTP email",
                    details={"error": [str(e)]}
                )
        return Response({
            "success": True,
            "message": "Registration successful! Please verify your email with the OTP sent to your inbox",
            "user": {
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)
    return error_response(code=400, details=serializer.errors)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User Login
    Required fields: email, password
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        try:
            is_verified = user.is_verified
            profile = user.user_profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=user, 
                full_name=user.email.split('@')[0], 
                business_name=""
            )
        profile_serializer = UserProfileSerializer(profile)
        return Response({
            "success": True,
            "message": "Login successful",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "email": user.email,
                "role": user.role,
                "is_verified": is_verified,
                "profile": profile_serializer.data
            }
        }, status=status.HTTP_200_OK)
    return error_response(code=401, details=serializer.errors)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_users(request):
    users = User.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    GET: Retrieve user profile
    PUT: Update user profile (supports file upload for profile picture)
    """
    try:
        profile = request.user.user_profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(
            user=request.user,
            full_name=request.user.email.split('@')[0]
        )

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response({
            "success": True,
            "profile": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Handle both JSON and multipart form data
        serializer = UserProfileSerializer(
            profile, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Security: Only allow the user to update their own profile
            if profile.user != request.user:
                return error_response(
                    code=403,
                    message="You can only update your own profile"
                )
            
            # Save the updated profile
            updated_profile = serializer.save()
            
            return Response({
                "success": True,
                "message": "Profile updated successfully",
                "profile": UserProfileSerializer(updated_profile, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        
        return error_response(code=400, details=serializer.errors)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_otp(request):
    email = request.data.get('email')
    if not email:
        return error_response(
            code=400,
            details={"email": ["This field is required"]}
        )
    
    try:
        user = User.objects.get(email=email)
        if user.is_verified:
            return error_response(
                code=400,
                details={"email": ["This account is already verified"]}
            )
    except User.DoesNotExist:
        return error_response(
            code=404,
            details={"email": ["No user exists with this email"]}
        )
    
    otp = generate_otp()
    otp_data = {'email': email, 'otp': otp}
    OTP.objects.filter(email=email).delete()
    serializer = OTPSerializer(data=otp_data)
    if serializer.is_valid():
        serializer.save()
        try:
            send_otp_email(email=email, otp=otp)
        except Exception as e:
            return error_response(
                code=500,
                message="Failed to send OTP email",
                details={"error": [str(e)]}
            )
        return Response({"message": "OTP sent to your email"}, status=status.HTTP_201_CREATED)
    return error_response(code=400, details=serializer.errors)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_reset(request):
    """
    Step 2 of password reset: Verify OTP
    Required fields: email, otp
    """
    email = request.data.get('email')
    otp_value = request.data.get('otp')
    
    if not email or not otp_value:
        details = {}
        if not email:
            details["email"] = ["This field is required"]
        if not otp_value:
            details["otp"] = ["This field is required"]
        return error_response(code=400, details=details)
    
    try:
        otp_obj = OTP.objects.get(email=email)
        if otp_obj.otp != otp_value:
            return error_response(
                code=400,
                details={"otp": ["The provided OTP is invalid"]}
            )
        if otp_obj.is_expired():
            return error_response(
                code=400,
                details={"otp": ["The OTP has expired. Please request a new one"]}
            )
        return Response({
            "success": True,
            "message": "OTP verified successfully. You can now reset your password"
        }, status=status.HTTP_200_OK)
    except OTP.DoesNotExist:
        return error_response(
            code=404,
            details={"otp": ["No valid OTP found. Please request password reset again"]}
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    email = request.data.get('email')
    otp_value = request.data.get('otp')
    
    if not email or not otp_value:
        details = {}
        if not email:
            details["email"] = ["This field is required"]
        if not otp_value:
            details["otp"] = ["This field is required"]
        return error_response(code=400, details=details)
    
    try:
        otp_obj = OTP.objects.get(email=email)
        if otp_obj.otp != otp_value:
            return error_response(
                code=400,
                details={"otp": ["The provided OTP is invalid"]}
            )
        if otp_obj.is_expired():
            return error_response(
                code=400,
                details={"otp": ["The OTP has expired"]}
            )
        
        # Verify the user
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return error_response(
                    code=400,
                    details={"email": ["This account is already verified"]}
                )
            user.is_verified = True
            user.save()
            otp_obj.delete()
            return Response({"message": "Email verified successfully. You can now log in"})
        except User.DoesNotExist:
            return error_response(
                code=404,
                details={"email": ["No user exists with this email"]}
            )
    except OTP.DoesNotExist:
        return error_response(
            code=404,
            details={"email": ["No OTP found for this email"]}
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Step 1 of password reset: Request OTP via email
    Required field: email
    """
    email = request.data.get('email')
    if not email:
        return error_response(
            code=400,
            details={"email": ["This field is required"]}
        )
    
    try:
        user = User.objects.get(email=email)
        if not user.is_verified:
            return error_response(
                code=400,
                details={"email": ["Please verify your email before resetting your password"]}
            )
    except User.DoesNotExist:
        return error_response(
            code=404,
            details={"email": ["No user exists with this email"]}
        )

    # Generate and send OTP
    otp = generate_otp()
    otp_data = {'email': email, 'otp': otp}
    OTP.objects.filter(email=email).delete()
    serializer = OTPSerializer(data=otp_data)
    if serializer.is_valid():
        serializer.save()
        try:
            send_otp_email(email=email, otp=otp)
        except Exception as e:
            return error_response(
                code=500,
                message="Failed to send OTP email",
                details={"error": [str(e)]}
            )
        return Response({
            "success": True,
            "message": "Password reset OTP sent to your email. Please check your inbox"
        }, status=status.HTTP_200_OK)
    return error_response(code=400, details=serializer.errors)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Step 3 of password reset: Verify OTP and set new password
    Required fields: email, otp, new_password, confirm_password
    """
    serializer = PasswordResetSerializer(data=request.data)
    
    if not serializer.is_valid():
        return error_response(code=400, details=serializer.errors)
    
    email = serializer.validated_data['email']
    otp_value = serializer.validated_data['otp']
    new_password = serializer.validated_data['new_password']

    try:
        # Verify OTP exists and is valid
        otp_obj = OTP.objects.get(email=email)
        if otp_obj.otp != otp_value:
            return error_response(
                code=400,
                details={"otp": ["The provided OTP is invalid"]}
            )
        
        if otp_obj.is_expired():
            return error_response(
                code=400,
                details={"otp": ["The OTP has expired. Please request a new one"]}
            )
        
        # Get user and verify account
        user = User.objects.get(email=email)
        if not user.is_verified:
            return error_response(
                code=400,
                details={"email": ["Please verify your email before resetting your password"]}
            )
        
        # Validate password strength
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return error_response(
                code=400,
                details={"new_password": e.messages}
            )

        # Update password and delete OTP
        user.set_password(new_password)
        user.save()
        otp_obj.delete()
        
        return Response({
            'success': True,
            'message': 'Password reset successful. You can now login with your new password'
        }, status=status.HTTP_200_OK)
        
    except OTP.DoesNotExist:
        return error_response(
            code=404,
            details={"otp": ["No valid OTP found. Please request password reset again"]}
        )
    except User.DoesNotExist:
        return error_response(
            code=404,
            details={"email": ["No user exists with this email"]}
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        details = {}
        if not current_password:
            details["current_password"] = ["This field is required"]
        if not new_password:
            details["new_password"] = ["This field is required"]
        return error_response(code=400, details=details)

    user = request.user
    if not user.check_password(current_password):
        return error_response(
            code=400,
            details={"current_password": ["The current password is incorrect"]}
        )

    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return error_response(
            code=400,
            details={"new_password": e.messages}
        )

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ No auth required to refresh token
def refresh_token(request):
    """
    Endpoint to refresh JWT tokens.
    """
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return Response({
            "error": True,
            "message": "Refresh token is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh = RefreshToken(refresh_token)
        new_access = str(refresh.access_token)
        new_refresh = str(refresh)  # new refresh token (if needed)

        return Response({
            
            "message": "Token refreshed successfully",
            "access_token": new_access,
            "refresh_token": new_refresh
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": True,
            "message": "Failed to refresh token",
            "details": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    """
    Delete a user and their profile (Admin only)
    Deleting CustomUser automatically deletes UserProfile due to CASCADE
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        email = user.email  # Store for response
        user_name = f"{user.user_profile.full_name}" if hasattr(user, 'user_profile') and user.user_profile.full_name else email
        
        # Delete CustomUser (automatically deletes UserProfile due to CASCADE)
        user.delete()
        
        return Response({
            "error": False,
            "message": f"User {user_name} ({email}) and their profile deleted successfully"
        }, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
        return error_response(
            code=404,
            message="User not found",
            details={"user_id": [f"No user found with ID {user_id}"]}
        )
    except Exception as e:
        return error_response(
            code=500,
            message="Failed to delete user",
            details={"error": [str(e)]}
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_own_account(request):
    """
    Allow users to delete their own account
    """
    try:
        user = request.user
        email = user.email
        user_name = f"{user.user_profile.full_name}" if hasattr(user, 'user_profile') and user.user_profile.full_name else email
        
        # Delete CustomUser (automatically deletes UserProfile due to CASCADE)
        user.delete()
        
        return Response({
            "error": False,
            "message": f"Your account {user_name} ({email}) has been deleted successfully"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return error_response(
            code=500,
            message="Failed to delete account",
            details={"error": [str(e)]}
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def onboarding_progress(request):
    """
    Handle onboarding progress:
    GET: Retrieve current user's onboarding progress
    POST: Create new onboarding progress for the user
    """
    user = request.user
    
    if request.method == 'GET':
        try:
            # Get existing onboarding progress
            progress = OnboardingProgress.objects.get(user=user)
            serializer = OnboardingProgressSerializer(progress, context={'request': request})
            
            return Response({
                "error": False,
                "message": "Onboarding progress retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except OnboardingProgress.DoesNotExist:
            return Response({
                "error": False,
                "message": "No onboarding progress found. You can start your onboarding process.",
                "data": None
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return error_response(
                code=500,
                message="Failed to retrieve onboarding progress",
                details={"error": [str(e)]}
            )
    
    elif request.method == 'POST':
        try:
            # Check if user already has onboarding progress
            existing_progress = OnboardingProgress.objects.filter(user=user).first()
            if existing_progress:
                return error_response(
                    code=400,
                    message="Onboarding progress already exists. Use PUT method to update.",
                    details={"user": ["User already has onboarding progress"]}
                )
            
            # Create new onboarding progress
            serializer = OnboardingProgressSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                progress = serializer.save()
                
                return Response({
                    "error": False,
                    "message": "Onboarding progress created successfully",
                    "data": OnboardingProgressSerializer(progress, context={'request': request}).data
                }, status=status.HTTP_201_CREATED)
            
            return error_response(
                code=400,
                message="Invalid data provided",
                details=serializer.errors
            )
        
        except Exception as e:
            return error_response(
                code=500,
                message="Failed to create onboarding progress",
                details={"error": [str(e)]}
            )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def onboarding_update(request):
    """
    Update user's onboarding progress
    """
    user = request.user
    
    try:
        # Get existing onboarding progress
        try:
            progress = OnboardingProgress.objects.get(user=user)
        except OnboardingProgress.DoesNotExist:
            return error_response(
                code=404,
                message="Onboarding progress not found. Please create onboarding progress first.",
                details={"user": ["No onboarding progress found for this user"]}
            )
        
        # Update onboarding progress
        serializer = OnboardingProgressSerializer(
            progress, 
            data=request.data, 
            partial=True,  # Allow partial updates
            context={'request': request}
        )
        
        if serializer.is_valid():
            updated_progress = serializer.save()
            
            # Check if onboarding is completed
            completion_message = ""
            if updated_progress.is_completed:
                completion_message = " Congratulations! Your onboarding is now complete."
            
            return Response({
                "error": False,
                "message": f"Onboarding progress updated successfully.{completion_message}",
                "data": OnboardingProgressSerializer(updated_progress, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        
        return error_response(
            code=400,
            message="Invalid data provided",
            details=serializer.errors
        )
    
    except Exception as e:
        return error_response(
            code=500,
            message="Failed to update onboarding progress",
            details={"error": [str(e)]}
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_onboarding_progress(request):
    """
    GET /api/auth/onboarding/get/ - Retrieve user's onboarding progress
    """
    user = request.user
    
    try:
        # Get existing onboarding progress
        progress = OnboardingProgress.objects.get(user=user)
        serializer = OnboardingProgressSerializer(progress, context={'request': request})
        
        return Response({
            "error": False,
            "message": "Onboarding progress retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    except OnboardingProgress.DoesNotExist:
        return error_response(
            code=404,
            message="No onboarding progress found. Please start your onboarding process.",
            details={"user": ["No onboarding progress found for this user"]}
        )
    
    except Exception as e:
        return error_response(
            code=500,
            message="Failed to retrieve onboarding progress",
            details={"error": [str(e)]}
        )
        
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Handle Google OAuth login/signup
        Creates new user if doesn't exist, logs in existing user
        """
        token = request.data.get("id_token")
        
        if not token:
            return error_response(
                code=400,
                message="Google ID token is required",
                details={"id_token": ["This field is required"]}
            )
        
        try:
            # Verify Google token
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            
            # Extract user info from Google
            email = idinfo.get("email")
            full_name = idinfo.get("name", "")
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")
            
            if not email:
                return error_response(
                    code=400,
                    message="Email not provided by Google",
                    details={"email": ["Email is required from Google account"]}
                )
            
            # Check if user exists
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'is_verified': True,  # Google accounts are pre-verified
                    'role': 'restaurant_owner',  # Default role, can be updated later
                }
            )
            
            if created:
                # New user - create profile
                UserProfile.objects.create(
                    user=user,
                    full_name=full_name or f"{first_name} {last_name}".strip() or email.split('@')[0],
                    business_name=""  # Can be filled during onboarding
                )
                message = "Account created and logged in successfully"
            else:
                # Existing user
                message = "Logged in successfully"
                # Ensure user is verified (in case they registered via email first)
                if not user.is_verified:
                    user.is_verified = True
                    user.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Get user profile
            try:
                profile = user.user_profile
            except UserProfile.DoesNotExist:
                # Create profile if missing
                profile = UserProfile.objects.create(
                    user=user,
                    full_name=full_name or email.split('@')[0],
                    business_name=""
                )
            
            profile_serializer = UserProfileSerializer(profile)
            
            return Response({
                "success": True,
                "message": message,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": {
                    "email": user.email,
                    "role": user.role,
                    "is_verified": user.is_verified,
                    "profile": profile_serializer.data
                },
                "is_new_user": created
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            # Invalid token
            return error_response(
                code=400,
                message="Invalid Google token",
                details={"id_token": [str(e)]}
            )
        except Exception as e:
            # Other errors
            return error_response(
                code=500,
                message="Google authentication failed",
                details={"error": [str(e)]}
            )