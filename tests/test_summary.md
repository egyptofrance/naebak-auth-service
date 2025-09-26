# Auth Service Test Summary

**Service:** naebak-auth-service  
**Test Date:** 2025-09-26T04:51:44.949268  
**Status:** READY  

## Results

- **Total Tests:** 9
- **Passed:** 7
- **Failed:** 0
- **Success Rate:** 77.8%

## Test Details

- ✅ **File Structure** (0.04ms): All required files present: 8//8
- ✅ **Python Syntax** (61.71ms): All 66 Python files have valid syntax
- ✅ **Dependencies** (47.22ms): All key dependencies available: 3 modules
- ⚠️ **Model Structure** (0.21ms): Models: ['User', 'Citizen']. Imports: ['from django.db import models', 'from django.contrib.auth']
- ✅ **API Views** (0.1ms): API views found: ['register_user', 'login_user', 'logout_user']. REST imports: 4
- ✅ **URL Configuration** (0.04ms): URL files: ['config/urls.py', 'users/urls.py']. Patterns: ['urlpatterns defined', 'path() usage found', 'auth endpoints defined']
- ✅ **Security Features** (0.12ms): Security features found: ['JWT authentication', 'Permission classes', 'Authentication logic', 'JWT authentication', 'CORS configuration', 'Secret key configuration']
- ⚠️ **Code Quality** (7.85ms): Quality score: 61.2%. Metrics: {'total_lines': 8878, 'python_files': 59, 'docstrings': 476, 'comments': 520, 'functions': 268, 'classes': 145}
- ✅ **Django Check** (861.1ms): Django check passed. Output: 
