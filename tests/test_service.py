#!/usr/bin/env python3
"""
Naebak Auth Service - Comprehensive Test Suite
==============================================

This test suite validates the authentication service functionality,
code quality, and readiness for deployment.

Test Results are logged with timestamps and detailed information.
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Setup logging
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
    """Comprehensive test suite for authentication service"""
    
    def __init__(self):
        self.service_path = '/home/ubuntu/naebak-auth-service'
        self.test_results = {
            'service_name': 'naebak-auth-service',
            'test_timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_details': [],
            'service_status': 'UNKNOWN'
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
        elif status == 'WARNING':
            logger.warning(f"⚠️  {test_name}: {details}")
        else:
            self.test_results['tests_failed'] += 1
            logger.error(f"❌ {test_name}: {details}")
    
    def test_file_structure(self):
        """Test service file structure and organization"""
        start_time = time.time()
        
        try:
            required_files = [
                'manage.py',
                'config/settings.py',
                'config/urls.py',
                'config/__init__.py',
                'users/models.py',
                'users/views.py',
                'users/urls.py',
                'requirements.txt'
            ]
            
            missing_files = []
            existing_files = []
            
            for file_path in required_files:
                full_path = os.path.join(self.service_path, file_path)
                if os.path.exists(full_path):
                    existing_files.append(file_path)
                else:
                    missing_files.append(file_path)
            
            if not missing_files:
                status = 'PASSED'
                details = f'All required files present: {len(existing_files)}//{len(required_files)}'
            else:
                status = 'WARNING'
                details = f'Missing files: {missing_files}. Present: {existing_files}'
            
            duration = time.time() - start_time
            self.log_test_result('File Structure', status, details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result('File Structure', 'FAILED', f'Error: {str(e)}', duration)
    
    def test_python_syntax(self):
        """Test Python syntax in all Python files"""
        start_time = time.time()
        
        try:
            python_files = []
            syntax_errors = []
            
            # Find all Python files
            for root, dirs, files in os.walk(self.service_path):
                # Skip virtual environment and cache directories
                dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
                
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            # Check syntax for each file
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        compile(f.read(), py_file, 'exec')
                except SyntaxError as e:
                    syntax_errors.append(f"{py_file}: {str(e)}")
                except Exception as e:
                    syntax_errors.append(f"{py_file}: {str(e)}")
            
            if not syntax_errors:
                status = 'PASSED'
                details = f'All {len(python_files)} Python files have valid syntax'
            else:
                status = 'FAILED'
                details = f'Syntax errors in {len(syntax_errors)} files: {syntax_errors[:3]}'
            
            duration = time.time() - start_time
            self.log_test_result('Python Syntax', status, details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result('Python Syntax', 'FAILED', f'Error: {str(e)}', duration)
    
    def test_django_check(self):
        """Test Django configuration using manage.py check"""
        start_time = time.time()
        
        try:
            os.chdir(self.service_path)
            
            # Run Django check command
            result = subprocess.run(
                ['python3', 'manage.py', 'check'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                status = 'PASSED'
                details = f'Django check passed. Output: {result.stdout.strip()}'
            else:
                status = 'FAILED'
                details = f'Django check failed. Error: {result.stderr.strip()}'
            
            duration = time.time() - start_time
            self.log_test_result('Django Check', status, details, duration)
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log_test_result('Django Check', 'FAILED', 'Command timed out after 30 seconds', duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result('Django Check', 'FAILED', f'Error: {str(e)}', duration)
    
    def test_dependencies(self):
        """Test if required dependencies are available"""
        start_time = time.time()
        
        try:
            requirements_file = os.path.join(self.service_path, 'requirements.txt')
            
            if not os.path.exists(requirements_file):
                self.log_test_result('Dependencies', 'WARNING', 'requirements.txt not found', 0)
                return
            
            # Read requirements
            with open(requirements_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Test key imports
            import_tests = [
                ('django', 'Django framework'),
                ('rest_framework', 'Django REST Framework'),
                ('jwt', 'JWT token handling'),
            ]
            
            available_imports = []
            missing_imports = []
            
            for module, description in import_tests:
                try:
                    __import__(module)
                    available_imports.append(f"{module} ({description})")
                except ImportError:
                    missing_imports.append(f"{module} ({description})")
            
            if not missing_imports:
                status = 'PASSED'
                details = f'All key dependencies available: {len(available_imports)} modules'
            else:
                status = 'WARNING'
                details = f'Missing: {missing_imports}. Available: {available_imports}'
            
            duration = time.time() - start_time
            self.log_test_result('Dependencies', status, details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result('Dependencies', 'FAILED', f'Error: {str(e)}', duration)
    
    def test_model_structure(self):
        """Test model structure and imports"""
        start_time = time.time()
        
        try:
            models_file = os.path.join(self.service_path, 'users/models.py')
            
            if not os.path.exists(models_file):
                self.log_test_result('Model Structure', 'FAILED', 'users/models.py not found', 0)
                return
            
            # Read models file
            with open(models_file, 'r', encoding='utf-8') as f:
                models_content = f.read()
            
            # Check for key model classes
            expected_models = ['User', 'Citizen', 'Representative', 'Official', 'Administrator']
            found_models = []
            
            for model in expected_models:
                if f'class {model}' in models_content:
                    found_models.append(model)
            
            # Check for key imports
            expected_imports = ['from django.db import models', 'from django.contrib.auth']
            found_imports = []
            
            for import_stmt in expected_imports:
                if import_stmt in models_content:
                    found_imports.append(import_stmt)
            
            if len(found_models) >= 3 and len(found_imports) >= 1:
                status = 'PASSED'
                details = f'Models found: {found_models}. Imports: {len(found_imports)}'
            else:
                status = 'WARNING'
                details = f'Models: {found_models}. Imports: {found_imports}'
            
            duration = time.time() - start_time
            self.log_test_result('Model Structure', status, details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result('Model Structure', 'FAILED', f'Error: {str(e)}', duration)
    
    def test_api_views(self):
        """Test API views structure"""
        start_time = time.time()
        
        try:
            views_file = os.path.join(self.service_path, 'users/views.py')
            
            if not os.path.exists(views_file):
                self.log_test_result('API Views', 'FAILED', 'users/views.py not found', 0)
                return
            
            # Read views file
            with open(views_file, 'r', encoding='utf-8') as f:
                views_content = f.read()
            
            # Check for key view functions
            expected_views = ['register_user', 'login_user', 'logout_user', 'refresh_token']
            found_views = []
            
            for view in expected_views:
                if f'def {view}' in views_content:
                    found_views.append(view)
            
            # Check for REST framework imports
            rest_imports = [
                'from rest_framework',
                '@api_view',
                'Response',
                'status'
            ]
            
            found_rest_imports = sum(1 for imp in rest_imports if imp in views_content)
            
            if len(found_views) >= 2 and found_rest_imports >= 2:
                status = 'PASSED'
                details = f'API views found: {found_views}. REST imports: {found_rest_imports}'
            else:
                status = 'WARNING'
                details = f'Views: {found_views}. REST imports: {found_rest_imports}'
            
            duration = time.time() - start_time
            self.log_test_result('API Views', status, details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result('API Views', 'FAILED', f'Error: {str(e)}', duration)
    
    def test_url_configuration(self):
        """Test URL configuration"""
        start_time = time.time()
        
        try:
            # Check main URLs
            main_urls = os.path.join(self.service_path, 'config/urls.py')
            app_urls = os.path.join(self.service_path, 'users/urls.py')
            
            url_files_exist = []
            if os.path.exists(main_urls):
                url_files_exist.append('config/urls.py')
            if os.path.exists(app_urls):
                url_files_exist.append('users/urls.py')
            
            # Check URL patterns in app urls
            if os.path.exists(app_urls):
                with open(app_urls, 'r', encoding='utf-8') as f:
                    urls_content = f.read()
                
                url_patterns = []
                if 'urlpatterns' in urls_content:
                    url_patterns.append('urlpatterns defined')
                if 'path(' in urls_content:
                    url_patterns.append('path() usage found')
                if 'register' in urls_content or 'login' in urls_content:
                    url_patterns.append('auth endpoints defined')
            else:
                url_patterns = []
            
            if len(url_files_exist) >= 2 and len(url_patterns) >= 2:
                status = 'PASSED'
                details = f'URL files: {url_files_exist}. Patterns: {url_patterns}'
            else:
                status = 'WARNING'
                details = f'URL files: {url_files_exist}. Patterns: {url_patterns}'
            
            duration = time.time() - start_time
            self.log_test_result('URL Configuration', status, details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result('URL Configuration', 'FAILED', f'Error: {str(e)}', duration)
    
    def test_security_features(self):
        """Test security-related code"""
        start_time = time.time()
        
        try:
            # Check for security imports and features
            security_files = [
                'users/views.py',
                'config/settings.py'
            ]
            
            security_features = []
            
            for file_path in security_files:
                full_path = os.path.join(self.service_path, file_path)
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for security features
                    if 'JWT' in content or 'jwt' in content:
                        security_features.append('JWT authentication')
                    if 'permission_classes' in content:
                        security_features.append('Permission classes')
                    if 'authenticate' in content:
                        security_features.append('Authentication logic')
                    if 'CORS' in content:
                        security_features.append('CORS configuration')
                    if 'SECRET_KEY' in content:
                        security_features.append('Secret key configuration')
            
            if len(security_features) >= 3:
                status = 'PASSED'
                details = f'Security features found: {security_features}'
            elif len(security_features) >= 1:
                status = 'WARNING'
                details = f'Some security features found: {security_features}'
            else:
                status = 'FAILED'
                details = 'No security features detected'
            
            duration = time.time() - start_time
            self.log_test_result('Security Features', status, details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result('Security Features', 'FAILED', f'Error: {str(e)}', duration)
    
    def test_code_quality(self):
        """Test code quality metrics"""
        start_time = time.time()
        
        try:
            quality_metrics = {
                'total_lines': 0,
                'python_files': 0,
                'docstrings': 0,
                'comments': 0,
                'functions': 0,
                'classes': 0
            }
            
            # Analyze Python files
            for root, dirs, files in os.walk(self.service_path):
                dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'tests']]
                
                for file in files:
                    if file.endswith('.py'):
                        quality_metrics['python_files'] += 1
                        file_path = os.path.join(root, file)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                quality_metrics['total_lines'] += len(lines)
                                
                                for line in lines:
                                    line = line.strip()
                                    if line.startswith('"""') or line.startswith("'''"):
                                        quality_metrics['docstrings'] += 1
                                    elif line.startswith('#'):
                                        quality_metrics['comments'] += 1
                                    elif line.startswith('def '):
                                        quality_metrics['functions'] += 1
                                    elif line.startswith('class '):
                                        quality_metrics['classes'] += 1
                        except Exception:
                            continue
            
            # Calculate quality score
            if quality_metrics['total_lines'] > 0:
                comment_ratio = (quality_metrics['comments'] + quality_metrics['docstrings']) / quality_metrics['total_lines']
                quality_score = min(100, comment_ratio * 100 + 50)  # Base score + comment bonus
            else:
                quality_score = 0
            
            if quality_score >= 70:
                status = 'PASSED'
            elif quality_score >= 50:
                status = 'WARNING'
            else:
                status = 'FAILED'
            
            details = f'Quality score: {quality_score:.1f}%. Metrics: {quality_metrics}'
            
            duration = time.time() - start_time
            self.log_test_result('Code Quality', status, details, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result('Code Quality', 'FAILED', f'Error: {str(e)}', duration)
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("🔐 Starting Naebak Auth Service Tests")
        logger.info("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_file_structure,
            self.test_python_syntax,
            self.test_dependencies,
            self.test_model_structure,
            self.test_api_views,
            self.test_url_configuration,
            self.test_security_features,
            self.test_code_quality,
            self.test_django_check
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} failed: {e}")
        
        # Determine overall service status
        if self.test_results['tests_failed'] == 0:
            if self.test_results['tests_passed'] >= 7:
                self.test_results['service_status'] = 'READY'
            else:
                self.test_results['service_status'] = 'NEEDS_WORK'
        else:
            self.test_results['service_status'] = 'FAILED'
        
        # Generate summary
        self.generate_test_report()
        
        return self.test_results
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("=" * 60)
        logger.info("📋 AUTH SERVICE TEST SUMMARY")
        logger.info("=" * 60)
        
        total_tests = self.test_results['tests_run']
        passed_tests = self.test_results['tests_passed']
        failed_tests = self.test_results['tests_failed']
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"🔐 Service: {self.test_results['service_name']}")
        logger.info(f"📅 Timestamp: {self.test_results['test_timestamp']}")
        logger.info(f"📊 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"🎯 Service Status: {self.test_results['service_status']}")
        
        # Save detailed results to JSON
        results_file = os.path.join(self.service_path, 'tests', 'test_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Detailed results saved to {results_file}")
        
        # Create summary file
        summary_file = os.path.join(self.service_path, 'tests', 'test_summary.md')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Auth Service Test Summary\n\n")
            f.write(f"**Service:** {self.test_results['service_name']}  \n")
            f.write(f"**Test Date:** {self.test_results['test_timestamp']}  \n")
            f.write(f"**Status:** {self.test_results['service_status']}  \n\n")
            f.write(f"## Results\n\n")
            f.write(f"- **Total Tests:** {total_tests}\n")
            f.write(f"- **Passed:** {passed_tests}\n")
            f.write(f"- **Failed:** {failed_tests}\n")
            f.write(f"- **Success Rate:** {success_rate:.1f}%\n\n")
            f.write(f"## Test Details\n\n")
            
            for test in self.test_results['test_details']:
                status_icon = "✅" if test['status'] == 'PASSED' else "⚠️" if test['status'] == 'WARNING' else "❌"
                f.write(f"- {status_icon} **{test['test_name']}** ({test['duration_ms']}ms): {test['details']}\n")
        
        logger.info(f"📋 Summary report saved to {summary_file}")
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
    if results['service_status'] == 'READY':
        print("🎉 SERVICE IS READY FOR DEPLOYMENT!")
        return 0
    elif results['service_status'] == 'NEEDS_WORK':
        print("⚠️  SERVICE NEEDS MINOR FIXES")
        return 1
    else:
        print("❌ SERVICE HAS CRITICAL ISSUES")
        return 2

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
