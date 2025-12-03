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
    OnboardingProgressSerializer,
    UserDocumentSerializer,
    SubscriptionSerializer,
    CalendarEventSerializer
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
import stripe
from django.conf import settings

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

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
                    'role': 'operations',  # Default role, can be updated later
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


# ==================== DOCUMENT MANAGEMENT APIs ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def document_management(request):
    """
    GET: List all documents for the authenticated user (with optional search)
    POST: Upload a new document
    """
    user = request.user
    
    if request.method == 'GET':
        # Get query parameter for search
        search_query = request.GET.get('search', '').strip()
        
        # Get all documents for the user
        documents = user.documents.all()
        
        # Apply search filter if provided
        if search_query:
            documents = documents.filter(file_name__icontains=search_query)
        
        # Serialize the documents
        from .serializers import UserDocumentSerializer
        serializer = UserDocumentSerializer(documents, many=True, context={'request': request})
        
        return Response({
            "error": False,
            "message": "Documents retrieved successfully",
            "count": documents.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        from .serializers import UserDocumentSerializer
        
        # Create new document
        serializer = UserDocumentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            document = serializer.save()
            
            return Response({
                "error": False,
                "message": "Document uploaded successfully",
                "data": UserDocumentSerializer(document, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return error_response(
            code=400,
            message="Invalid data provided",
            details=serializer.errors
        )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def document_detail(request, document_id):
    """
    GET: Retrieve a specific document
    PUT: Update document metadata (not the file itself)
    DELETE: Delete a document
    """
    from .models import UserDocument
    from .serializers import UserDocumentSerializer
    
    user = request.user
    
    try:
        document = UserDocument.objects.get(id=document_id, user=user)
    except UserDocument.DoesNotExist:
        return error_response(
            code=404,
            message="Document not found",
            details={"document_id": [f"No document found with ID {document_id}"]}
        )
    
    if request.method == 'GET':
        serializer = UserDocumentSerializer(document, context={'request': request})
        return Response({
            "error": False,
            "message": "Document retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Only allow updating metadata, not the file
        serializer = UserDocumentSerializer(
            document,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            updated_document = serializer.save()
            
            return Response({
                "error": False,
                "message": "Document updated successfully",
                "data": UserDocumentSerializer(updated_document, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        
        return error_response(
            code=400,
            message="Invalid data provided",
            details=serializer.errors
        )
    
    elif request.method == 'DELETE':
        document_name = document.file_name
        document.delete()
        
        return Response({
            "error": False,
            "message": f"Document '{document_name}' deleted successfully"
        }, status=status.HTTP_200_OK)


# ==================== SUBSCRIPTION APIs ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def subscription_management(request):
    """
    GET: Retrieve current user's subscription
    POST: Create or update subscription
    """
    from .models import Subscription
    from .serializers import SubscriptionSerializer
    
    user = request.user
    
    if request.method == 'GET':
        try:
            subscriptions = Subscription.objects.filter(user=user)
            serializer = SubscriptionSerializer(subscriptions, many=True, context={'request': request})
            
            return Response({
                "error": False,
                "message": "Subscriptions retrieved successfully",
                "data": serializer.data,
                "count": subscriptions.count()
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "error": False,
                "message": "No subscription found. Please create one.",
                "data": [],
                "count": 0
            }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Check if user already has a subscription
        existing_subscription = Subscription.objects.filter(user=user).first()
        
        if existing_subscription:
            # Update existing subscription
            serializer = SubscriptionSerializer(
                existing_subscription,
                data=request.data,
                partial=True,
                context={'request': request}
            )
        else:
            # Create new subscription
            serializer = SubscriptionSerializer(
                data=request.data,
                context={'request': request}
            )
        
        if serializer.is_valid():
            subscription = serializer.save()
            
            message = "Subscription updated successfully" if existing_subscription else "Subscription created successfully"
            
            return Response({
                "error": False,
                "message": message,
                "data": SubscriptionSerializer(subscription, context={'request': request}).data
            }, status=status.HTTP_200_OK if existing_subscription else status.HTTP_201_CREATED)
        
        return error_response(
            code=400,
            message="Invalid data provided",
            details=serializer.errors
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def subscription_cancel(request):
    """
    Cancel user's subscription
    """
    from .models import Subscription
    
    user = request.user
    
    try:
        subscription = Subscription.objects.get(user=user)
        subscription.status = 'cancelled'
        subscription.auto_renew = False
        subscription.save()
        
        return Response({
            "error": False,
            "message": "Subscription cancelled successfully"
        }, status=status.HTTP_200_OK)
    
    except Subscription.DoesNotExist:
        return error_response(
            code=404,
            message="No active subscription found",
            details={"subscription": ["User does not have a subscription"]}
        )


# ==================== STRIPE PAYMENT APIs ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stripe_products(request):
    """
    Admin endpoint to create Stripe products and prices for subscriptions
    This should be run once to set up the products in Stripe
    """
    try:
        products_created = []
        
        # Define subscription plans
        plans = {
            'starter': {
                'name': 'Starter Plan',
                'description': 'Free trial for 10 days - Perfect for getting started',
                'price': 0,
                'currency': 'usd',
            },
            'professional': {
                'name': 'Professional Plan',
                'description': 'Premium features for 1 month at $29',
                'price': 2900,  # $29.00 in cents
                'currency': 'usd',
            },
            'enterprise': {
                'name': 'Enterprise Plan',
                'description': 'Full access for 6 months at $69',
                'price': 6900,  # $69.00 in cents
                'currency': 'usd',
            }
        }
        
        for plan_key, plan_data in plans.items():
            # Create product
            product = stripe.Product.create(
                name=plan_data['name'],
                description=plan_data['description'],
            )
            
            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=plan_data['price'],
                currency=plan_data['currency'],
            )
            
            products_created.append({
                'plan': plan_key,
                'product_id': product.id,
                'price_id': price.id,
                'amount': plan_data['price'] / 100,
                'currency': plan_data['currency']
            })
        
        return Response({
            "error": False,
            "message": "Stripe products created successfully",
            "data": products_created,
            "price_ids": {
                'starter': products_created[0]['price_id'],
                'professional': products_created[1]['price_id'],
                'enterprise': products_created[2]['price_id']
            }
        }, status=status.HTTP_200_OK)
    
    except stripe.error.StripeError as e:
        return error_response(
            code=400,
            message="Stripe error occurred",
            details={"error": [str(e)]}
        )
    except Exception as e:
        return error_response(
            code=500,
            message="Failed to create products",
            details={"error": [str(e)]}
        )


def get_stripe_price_ids():
    """
    Get Stripe price IDs from Stripe products dynamically
    Returns dict with plan names as keys and price IDs as values
    """
    try:
        products = stripe.Product.list(limit=100)
        price_ids = {}
        
        for product in products.data:
            product_name_lower = product.name.lower()
            
            # Get the price for this product
            prices = stripe.Price.list(product=product.id, limit=1)
            if prices.data:
                price_id = prices.data[0].id
                
                if 'starter' in product_name_lower:
                    price_ids['starter'] = price_id
                elif 'professional' in product_name_lower:
                    price_ids['professional'] = price_id
                elif 'enterprise' in product_name_lower:
                    price_ids['enterprise'] = price_id
        
        return price_ids
    except Exception as e:
        return {}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """
    Create Stripe checkout session for subscription payment
    Required: plan ('starter', 'professional', or 'enterprise')
    """
    from .models import Subscription
    from django.utils import timezone
    from datetime import timedelta
    
    user = request.user
    plan = request.data.get('plan')
    
    if not plan or plan not in ['starter', 'professional', 'enterprise']:
        return error_response(
            code=400,
            message="Invalid plan",
            details={"plan": ["Please provide a valid plan: starter, professional, or enterprise"]}
        )
    
    # Get price IDs from Stripe dynamically
    stripe_price_ids = get_stripe_price_ids()
    
    # Define plan details
    plan_details = {
        'starter': {
            'price_id': stripe_price_ids.get('starter', ''),
            'price': 0,
            'days': 10,
            'is_trial': True,
            'name': 'Starter Plan'
        },
        'professional': {
            'price_id': stripe_price_ids.get('professional', ''),
            'price': 29.00,
            'days': 30,
            'is_trial': False,
            'name': 'Professional Plan'
        },
        'enterprise': {
            'price_id': stripe_price_ids.get('enterprise', ''),
            'price': 69.00,
            'days': 180,
            'is_trial': False,
            'name': 'Enterprise Plan'
        },
    }
    
    current_plan = plan_details[plan]
    
    # For free starter plan, create subscription directly
    if plan == 'starter':
        try:
            # Check if user already has a subscription
            existing_subscription = Subscription.objects.filter(user=user).first()
            
            if existing_subscription:
                existing_subscription.plan = plan
                existing_subscription.price = current_plan['price']
                existing_subscription.status = 'active'
                existing_subscription.end_date = timezone.now() + timedelta(days=current_plan['days'])
                existing_subscription.is_trial = current_plan['is_trial']
                existing_subscription.save()
                subscription = existing_subscription
            else:
                subscription = Subscription.objects.create(
                    user=user,
                    plan=plan,
                    price=current_plan['price'],
                    status='active',
                    end_date=timezone.now() + timedelta(days=current_plan['days']),
                    is_trial=current_plan['is_trial'],
                )
            
            from .serializers import SubscriptionSerializer
            return Response({
                "error": False,
                "message": "Starter subscription activated successfully (Free Trial)",
                "data": SubscriptionSerializer(subscription, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return error_response(
                code=500,
                message="Failed to create subscription",
                details={"error": [str(e)]}
            )
    
    # For paid plans, create Stripe checkout session
    try:
        # Check if price ID is configured
        if not current_plan['price_id']:
            return error_response(
                code=500,
                message="Stripe price not configured",
                details={"error": ["Please run /api/auth/subscription/stripe/setup/ first to create products"]}
            )
        
        # Get or create subscription record
        existing_subscription = Subscription.objects.filter(user=user).first()
        if not existing_subscription:
            # Create pending subscription
            subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                price=current_plan['price'],
                status='expired',  # Will be updated by webhook
                end_date=timezone.now() + timedelta(days=current_plan['days']),
                is_trial=current_plan['is_trial'],
                stripe_price_id=current_plan['price_id']
            )
        else:
            subscription = existing_subscription
            subscription.plan = plan
            subscription.price = current_plan['price']
            subscription.end_date = timezone.now() + timedelta(days=current_plan['days'])
            subscription.is_trial = current_plan['is_trial']
            subscription.stripe_price_id = current_plan['price_id']
            subscription.save()
        
        # Create Stripe checkout session
        YOUR_DOMAIN = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': current_plan['price_id'],
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/api/auth/subscription/payment/success/',
            cancel_url=YOUR_DOMAIN + '/api/auth/subscription/payment/cancel/',
            client_reference_id=str(user.id),
            metadata={
                'plan': plan,
                'user_id': str(user.id),
            }
        )
        
        # Save session ID
        subscription.stripe_session_id = checkout_session.id
        subscription.save()
        
        return Response({
            "error": False,
            "message": "Checkout session created successfully",
            "data": {
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'plan': current_plan['name'],
                'price': current_plan['price']
            }
        }, status=status.HTTP_200_OK)
    
    except stripe.error.StripeError as e:
        return error_response(
            code=400,
            message="Stripe error occurred",
            details={"error": [str(e)]}
        )
    except Exception as e:
        return error_response(
            code=500,
            message="Failed to create checkout session",
            details={"error": [str(e)]}
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_success(request):
    """
    Payment success redirect endpoint
    """
    from django.shortcuts import redirect
    # You can change this URL to your frontend success page
    return redirect('http://localhost:3000/subscription/success')


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_cancel(request):
    """
    Payment cancellation redirect endpoint
    """
    from django.shortcuts import redirect
    # You can change this URL to your frontend cancel page
    return redirect('http://localhost:3000/subscription/cancel')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_detail(request, subscription_id):
    """
    Get details of a specific subscription by ID
    """
    from .models import Subscription
    from .serializers import SubscriptionSerializer
    
    user = request.user
    
    try:
        subscription = Subscription.objects.get(id=subscription_id, user=user)
        serializer = SubscriptionSerializer(subscription, context={'request': request})
        
        return Response({
            "error": False,
            "message": "Subscription details retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Subscription.DoesNotExist:
        return error_response(
            code=404,
            message="Subscription not found",
            details={"subscription_id": [f"No subscription found with ID {subscription_id}"]}
        )


# ==================== CALENDAR APIs ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def calendar_events(request):
    """
    GET: List all calendar events for the authenticated user
    POST: Create a new calendar event
    """
    from .models import CalendarEvent
    from .serializers import CalendarEventSerializer
    
    user = request.user
    
    if request.method == 'GET':
        # Get query parameters for filtering
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        event_type = request.GET.get('event_type')
        
        # Get all events for the user
        events = CalendarEvent.objects.filter(user=user)
        
        # Apply filters if provided
        if start_date:
            from django.utils.dateparse import parse_datetime
            start_dt = parse_datetime(start_date)
            if start_dt:
                events = events.filter(start_date__gte=start_dt)
        
        if end_date:
            from django.utils.dateparse import parse_datetime
            end_dt = parse_datetime(end_date)
            if end_dt:
                events = events.filter(end_date__lte=end_dt)
        
        if event_type:
            events = events.filter(event_type=event_type)
        
        # Serialize the events
        serializer = CalendarEventSerializer(events, many=True, context={'request': request})
        
        return Response({
            "error": False,
            "message": "Calendar events retrieved successfully",
            "count": events.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Create new calendar event
        serializer = CalendarEventSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            event = serializer.save()
            
            return Response({
                "error": False,
                "message": "Calendar event created successfully",
                "data": CalendarEventSerializer(event, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return error_response(
            code=400,
            message="Invalid data provided",
            details=serializer.errors
        )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def calendar_event_detail(request, event_id):
    """
    GET: Retrieve a specific calendar event
    PUT: Update a calendar event
    DELETE: Delete a calendar event
    """
    from .models import CalendarEvent
    from .serializers import CalendarEventSerializer
    
    user = request.user
    
    try:
        event = CalendarEvent.objects.get(id=event_id, user=user)
    except CalendarEvent.DoesNotExist:
        return error_response(
            code=404,
            message="Calendar event not found",
            details={"event_id": [f"No event found with ID {event_id}"]}
        )
    
    if request.method == 'GET':
        serializer = CalendarEventSerializer(event, context={'request': request})
        return Response({
            "error": False,
            "message": "Calendar event retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = CalendarEventSerializer(
            event,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            updated_event = serializer.save()
            
            return Response({
                "error": False,
                "message": "Calendar event updated successfully",
                "data": CalendarEventSerializer(updated_event, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        
        return error_response(
            code=400,
            message="Invalid data provided",
            details=serializer.errors
        )
    
    elif request.method == 'DELETE':
        event_title = event.title
        event.delete()
        
        return Response({
            "error": False,
            "message": f"Calendar event '{event_title}' deleted successfully"
        }, status=status.HTTP_200_OK)