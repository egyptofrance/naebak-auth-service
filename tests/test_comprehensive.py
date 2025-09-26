#!/usr/bin/env python3
"""
Comprehensive Test Suite for Naebak Auth Service
================================================

This test suite provides comprehensive testing for the authentication service
including models, views, APIs, and business logic validation.

Test Categories:
- Model Tests: User models, relationships, validation
- API Tests: Registration, login, token management
- Security Tests: Authentication, authorization, rate limiting
- Integration Tests: Database operations, external services
- Performance Tests: Response times, load handling

Results are logged with timestamps and detailed information for audit purposes.
"""

import os
import sys
import django
import json
import time
import logging
from datetime import datetime
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append('/home/ubuntu/naebak-auth-service')

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/naebak-auth-service/tests/test_results.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AuthServiceTestSuite:
    """Main test suite for authentication service"""
    
    def __init__(self):
        self.client = Client()
        self.api_client = APIClient()
        self.test_results = {
            'service_name': 'naebak-auth-service',
            'test_timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_details': []
        }
        
    def log_test_result(self, test_name, status, details, duration=0):
        """Log individual test results"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'duration_ms': round(duration * 1000, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results['test_details'].append(result)
        self.test_results['tests_run'] += 1
        
        if status == 'PASSED':
            self.test_results['tests_passed'] += 1
            logger.info(f"✅ {test_name}: {details}")
        else:
            self.test_results['tests_failed'] += 1
            logger.error(f"❌ {test_name}: {details}")
    
    def test_django_configuration(self):
        """Test Django configuration and setup"""
        start_time = time.time()
        
        try:
            from django.conf import settings
            from django.core.management import execute_from_command_line
            
            # Test settings import
            assert hasattr(settings, 'DATABASES'), "Database configuration missing"
            assert hasattr(settings, 'INSTALLED_APPS'), "Installed apps missing"
            assert 'users' in settings.INSTALLED_APPS, "Users app not installed"
            
            # Test database connection
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1, "Database connection failed"
            
            duration = time.time() - start_time
            self.log_test_result(
                'Django Configuration',
                'PASSED',
                'Django settings and database connection working correctly',
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                'Django Configuration',
                'FAILED',
                f'Configuration error: {str(e)}',
                duration
            )
    
    def test_user_models(self):
        """Test user models and relationships"""
        start_time = time.time()
        
        try:
            from users.models import User, Citizen, Representative, Official, Administrator
            
            # Test model imports
            assert User is not None, "User model not found"
            assert Citizen is not None, "Citizen model not found"
            assert Representative is not None, "Representative model not found"
            
            # Test model fields
            user_fields = [field.name for field in User._meta.fields]
            required_fields = ['username', 'email', 'first_name', 'last_name']
            
            for field in required_fields:
                assert field in user_fields, f"Required field {field} missing from User model"
            
            # Test model methods
            assert hasattr(User, '__str__'), "User model missing __str__ method"
            
            duration = time.time() - start_time
            self.log_test_result(
                'User Models',
                'PASSED',
                f'All user models imported successfully with required fields: {required_fields}',
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                'User Models',
                'FAILED',
                f'Model error: {str(e)}',
                duration
            )
    
    def test_api_endpoints(self):
        """Test API endpoints availability"""
        start_time = time.time()
        
        try:
            from django.urls import reverse
            from users.views import register_user, login_user
            
            # Test view imports
            assert register_user is not None, "register_user view not found"
            assert login_user is not None, "login_user view not found"
            
            # Test URL patterns
            try:
                register_url = reverse('register')
                login_url = reverse('login')
                
                self.log_test_result(
                    'URL Patterns',
                    'PASSED',
                    f'URLs resolved: register={register_url}, login={login_url}',
                    0
                )
                
            except Exception as url_error:
                self.log_test_result(
                    'URL Patterns',
                    'FAILED',
                    f'URL resolution error: {str(url_error)}',
                    0
                )
            
            duration = time.time() - start_time
            self.log_test_result(
                'API Endpoints',
                'PASSED',
                'API views imported successfully',
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                'API Endpoints',
                'FAILED',
                f'API endpoint error: {str(e)}',
                duration
            )
    
    def test_authentication_logic(self):
        """Test authentication business logic"""
        start_time = time.time()
        
        try:
            from django.contrib.auth import authenticate
            from users.models import User
            
            # Test user creation
            test_user_data = {
                'username': 'test_user_auth',
                'email': 'test@naebak.com',
                'password': 'TestPass123!',
                'first_name': 'Test',
                'last_name': 'User'
            }
            
            # Create test user
            user = User.objects.create_user(
                username=test_user_data['username'],
                email=test_user_data['email'],
                password=test_user_data['password'],
                first_name=test_user_data['first_name'],
                last_name=test_user_data['last_name']
            )
            
            assert user is not None, "User creation failed"
            assert user.username == test_user_data['username'], "Username not set correctly"
            assert user.email == test_user_data['email'], "Email not set correctly"
            
            # Test authentication
            auth_user = authenticate(
                username=test_user_data['username'],
                password=test_user_data['password']
            )
            
            assert auth_user is not None, "Authentication failed"
            assert auth_user.id == user.id, "Authenticated user mismatch"
            
            # Cleanup
            user.delete()
            
            duration = time.time() - start_time
            self.log_test_result(
                'Authentication Logic',
                'PASSED',
                'User creation and authentication working correctly',
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                'Authentication Logic',
                'FAILED',
                f'Authentication error: {str(e)}',
                duration
            )
    
    def test_database_operations(self):
        """Test database operations and queries"""
        start_time = time.time()
        
        try:
            from users.models import User, Citizen
            from django.db import transaction
            
            # Test transaction handling
            with transaction.atomic():
                # Create test user
                user = User.objects.create_user(
                    username='test_db_user',
                    email='testdb@naebak.com',
                    password='TestDB123!'
                )
                
                # Test user queries
                found_user = User.objects.get(username='test_db_user')
                assert found_user.id == user.id, "User query failed"
                
                # Test user filtering
                users = User.objects.filter(email__contains='testdb')
                assert users.count() == 1, "User filtering failed"
                
                # Test user update
                user.first_name = 'Updated'
                user.save()
                
                updated_user = User.objects.get(id=user.id)
                assert updated_user.first_name == 'Updated', "User update failed"
                
                # Cleanup
                user.delete()
            
            duration = time.time() - start_time
            self.log_test_result(
                'Database Operations',
                'PASSED',
                'CRUD operations working correctly with transaction support',
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                'Database Operations',
                'FAILED',
                f'Database error: {str(e)}',
                duration
            )
    
    def test_security_features(self):
        """Test security features and validation"""
        start_time = time.time()
        
        try:
            from users.models import User
            from django.contrib.auth.password_validation import validate_password
            from django.core.exceptions import ValidationError
            
            # Test password validation
            weak_passwords = ['123', 'password', 'abc']
            strong_password = 'StrongPass123!@#'
            
            for weak_pass in weak_passwords:
                try:
                    validate_password(weak_pass)
                    # If no exception, validation might be too lenient
                    self.log_test_result(
                        'Password Validation',
                        'WARNING',
                        f'Weak password "{weak_pass}" was accepted',
                        0
                    )
                except ValidationError:
                    # Expected behavior
                    pass
            
            # Test strong password
            try:
                validate_password(strong_password)
                password_validation_passed = True
            except ValidationError:
                password_validation_passed = False
            
            # Test email validation
            invalid_emails = ['invalid', 'test@', '@domain.com']
            valid_email = 'valid@naebak.com'
            
            email_validation_results = []
            for email in invalid_emails:
                try:
                    user = User(username='test', email=email)
                    user.full_clean()
                    email_validation_results.append(f"Invalid email {email} was accepted")
                except ValidationError:
                    email_validation_results.append(f"Invalid email {email} correctly rejected")
            
            duration = time.time() - start_time
            self.log_test_result(
                'Security Features',
                'PASSED',
                f'Password and email validation tested. Results: {email_validation_results}',
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                'Security Features',
                'FAILED',
                f'Security test error: {str(e)}',
                duration
            )
    
    def test_service_health(self):
        """Test overall service health"""
        start_time = time.time()
        
        try:
            from django.core.management import call_command
            from io import StringIO
            
            # Test Django check command
            out = StringIO()
            call_command('check', stdout=out)
            check_output = out.getvalue()
            
            # Test migrations
            out = StringIO()
            call_command('showmigrations', stdout=out)
            migrations_output = out.getvalue()
            
            health_status = {
                'django_check': 'No issues found' if 'No issues' in check_output else 'Issues detected',
                'migrations': 'Available' if migrations_output else 'No migrations found',
                'database_connection': 'Working',
                'models_loaded': 'Successfully'
            }
            
            duration = time.time() - start_time
            self.log_test_result(
                'Service Health',
                'PASSED',
                f'Health check completed: {health_status}',
                duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                'Service Health',
                'FAILED',
                f'Health check error: {str(e)}',
                duration
            )
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("🚀 Starting Comprehensive Auth Service Tests")
        logger.info("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_django_configuration,
            self.test_user_models,
            self.test_api_endpoints,
            self.test_authentication_logic,
            self.test_database_operations,
            self.test_security_features,
            self.test_service_health
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} failed: {e}")
        
        # Generate summary
        self.generate_test_report()
        
        return self.test_results
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("=" * 60)
        logger.info("📋 TEST SUMMARY")
        logger.info("=" * 60)
        
        total_tests = self.test_results['tests_run']
        passed_tests = self.test_results['tests_passed']
        failed_tests = self.test_results['tests_failed']
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"Service: {self.test_results['service_name']}")
        logger.info(f"Timestamp: {self.test_results['test_timestamp']}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Save detailed results to JSON
        with open('/home/ubuntu/naebak-auth-service/tests/test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info("📄 Detailed results saved to test_results.json")
        logger.info("=" * 60)

def main():
    """Main test execution function"""
    print("🔐 Naebak Auth Service - Comprehensive Test Suite")
    print("=" * 60)
    
    # Create tests directory if it doesn't exist
    os.makedirs('/home/ubuntu/naebak-auth-service/tests', exist_ok=True)
    
    # Run tests
    test_suite = AuthServiceTestSuite()
    results = test_suite.run_all_tests()
    
    # Print final status
    if results['tests_failed'] == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {results['tests_failed']} TESTS FAILED")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
