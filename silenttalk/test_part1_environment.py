#!/usr/bin/env python3
"""
Part 1: Environment and Dependency Testing
Records all environment information for the Silent Talk test report.
"""

import subprocess
import sys
import os
import json
from datetime import datetime

TEST_RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "part": "Part 1 - Environment and Dependency Testing",
    "tests": {}
}

def run_command(cmd, description):
    """Run a shell command and record results."""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()
        error = result.stderr.strip()
        success = result.returncode == 0
        
        print(f"Return Code: {result.returncode}")
        print(f"Output:\n{output}")
        if error:
            print(f"Stderr:\n{error}")
        
        TEST_RESULTS["tests"][description] = {
            "command": cmd,
            "success": success,
            "returncode": result.returncode,
            "output": output,
            "error": error if error else None
        }
        return success, output
    except Exception as e:
        print(f"EXCEPTION: {e}")
        TEST_RESULTS["tests"][description] = {
            "command": cmd,
            "success": False,
            "error": str(e)
        }
        return False, str(e)

def main():
    print("#"*60)
    print("# PART 1: ENVIRONMENT AND DEPENDENCY TESTING")
    print("#"*60)
    
    os.chdir("d:/Semester - 4/Full Stack Development/SilentTalk - The Project/silenttalk")
    
    # 1.1 Python Environment
    print("\n" + "#"*60)
    print("# 1.1 PYTHON ENVIRONMENT")
    print("#"*60)
    
    run_command("python --version", "Python Version")
    run_command("python -m django --version", "Django Version")
    run_command("pip show mediapipe", "MediaPipe Version")
    run_command("pip show tensorflow", "TensorFlow Version")
    run_command("pip show opencv-python", "OpenCV Version")
    run_command("pip show scikit-learn", "scikit-learn Version")
    run_command("pip show numpy", "NumPy Version")
    run_command("pip freeze", "All Installed Packages")
    run_command("pip check", "Dependency Conflict Check")
    
    # Check virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"\n{'='*60}")
    print("TEST: Virtual Environment Check")
    print('='*60)
    print(f"In Virtual Environment: {in_venv}")
    print(f"sys.prefix: {sys.prefix}")
    if hasattr(sys, 'real_prefix'):
        print(f"sys.real_prefix: {sys.real_prefix}")
    if hasattr(sys, 'base_prefix'):
        print(f"sys.base_prefix: {sys.base_prefix}")
    TEST_RESULTS["tests"]["Virtual Environment Check"] = {
        "in_venv": in_venv,
        "prefix": sys.prefix,
        "base_prefix": getattr(sys, 'base_prefix', None)
    }
    
    # 1.2 Database Connectivity
    print("\n" + "#"*60)
    print("# 1.2 DATABASE CONNECTIVITY")
    print("#"*60)
    
    run_command("pg_isready", "PostgreSQL Server Status")
    run_command("python manage.py check", "Django System Check")
    run_command("python manage.py showmigrations", "Migration Status")
    run_command("python manage.py migrate --dry-run", "Migrate Dry Run")
    
    # Try database shell
    print(f"\n{'='*60}")
    print("TEST: Database Connection (dbshell)")
    print('='*60)
    try:
        # Just test the connection, don't actually open shell
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silenttalk.settings')
        django.setup()
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Database connection successful: {result}")
            TEST_RESULTS["tests"]["Database Connection"] = {
                "success": True,
                "result": result
            }
    except Exception as e:
        print(f"Database connection failed: {e}")
        TEST_RESULTS["tests"]["Database Connection"] = {
            "success": False,
            "error": str(e)
        }
    
    # 1.3 Model File Integrity
    print("\n" + "#"*60)
    print("# 1.3 MODEL FILE INTEGRITY")
    print("#"*60)
    
    model_files = {
        "model.p": "recognition/model.p",
        "gesture_recognizer.task": "recognition/static/recognition/gesture_recognizer.task"
    }
    
    for name, path in model_files.items():
        full_path = os.path.join(os.path.dirname(__file__), path)
        print(f"\n{'='*60}")
        print(f"TEST: {name} File Check")
        print('='*60)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"File exists: {full_path}")
            print(f"File size: {size} bytes ({size/1024/1024:.2f} MB)")
            TEST_RESULTS["tests"][f"{name} File Check"] = {
                "exists": True,
                "path": full_path,
                "size_bytes": size,
                "size_mb": round(size/1024/1024, 2)
            }
        else:
            print(f"File NOT found: {full_path}")
            TEST_RESULTS["tests"][f"{name} File Check"] = {
                "exists": False,
                "path": full_path
            }
    
    # Test loading model.p
    print(f"\n{'='*60}")
    print("TEST: Load model.p with pickle")
    print('='*60)
    try:
        import pickle
        import time
        model_path = os.path.join(os.path.dirname(__file__), "recognition", "model.p")
        start = time.time()
        with open(model_path, 'rb') as f:
            model_dict = pickle.load(f)
        elapsed = (time.time() - start) * 1000
        model = model_dict.get("model")
        print(f"Model loaded successfully in {elapsed:.2f} ms")
        print(f"Model type: {type(model)}")
        print(f"Model dict keys: {list(model_dict.keys())}")
        TEST_RESULTS["tests"]["Load model.p"] = {
            "success": True,
            "load_time_ms": round(elapsed, 2),
            "model_type": str(type(model)),
            "dict_keys": list(model_dict.keys())
        }
    except Exception as e:
        print(f"Failed to load model.p: {e}")
        import traceback
        traceback.print_exc()
        TEST_RESULTS["tests"]["Load model.p"] = {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    
    # Test loading gesture_recognizer.task
    print(f"\n{'='*60}")
    print("TEST: Load gesture_recognizer.task with MediaPipe")
    print('='*60)
    try:
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        import time
        
        model_path = os.path.join(os.path.dirname(__file__), "recognition", "static", "recognition", "gesture_recognizer.task")
        start = time.time()
        with open(model_path, "rb") as f:
            model_data = f.read()
        base_options = python.BaseOptions(model_asset_buffer=model_data)
        options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=2)
        recognizer = vision.GestureRecognizer.create_from_options(options)
        elapsed = (time.time() - start) * 1000
        print(f"Gesture recognizer loaded successfully in {elapsed:.2f} ms")
        TEST_RESULTS["tests"]["Load gesture_recognizer.task"] = {
            "success": True,
            "load_time_ms": round(elapsed, 2)
        }
    except Exception as e:
        print(f"Failed to load gesture_recognizer.task: {e}")
        import traceback
        traceback.print_exc()
        TEST_RESULTS["tests"]["Load gesture_recognizer.task"] = {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    
    # 1.4 Static Files and Assets
    print("\n" + "#"*60)
    print("# 1.4 STATIC FILES AND ASSETS")
    print("#"*60)
    
    # Count .sigml files
    signfiles_dir = os.path.join(os.path.dirname(__file__), "recognition", "static", "recognition", "SignFiles")
    if os.path.exists(signfiles_dir):
        sigml_files = [f for f in os.listdir(signfiles_dir) if f.endswith('.sigml')]
        sigml_count = len(sigml_files)
        print(f"\nSIGML files found: {sigml_count}")
        TEST_RESULTS["tests"]["SIGML File Count"] = {
            "count": sigml_count,
            "directory": signfiles_dir
        }
    else:
        print(f"SignFiles directory not found: {signfiles_dir}")
        TEST_RESULTS["tests"]["SIGML File Count"] = {
            "count": 0,
            "error": "Directory not found"
        }
    
    # Check words.txt
    words_path = os.path.join(os.path.dirname(__file__), "recognition", "static", "recognition", "words.txt")
    print(f"\n{'='*60}")
    print("TEST: words.txt Analysis")
    print('='*60)
    if os.path.exists(words_path):
        with open(words_path, 'r') as f:
            content = f.read()
        # Parse Python-style list
        import re
        words = [w.strip().lower() for w in re.findall(r"'([^']+)'", content)]
        word_count = len(words)
        print(f"words.txt exists")
        print(f"Word count: {word_count}")
        print(f"First 10 words: {words[:10]}")
        TEST_RESULTS["tests"]["words.txt"] = {
            "exists": True,
            "word_count": word_count,
            "sample_words": words[:20]
        }
    else:
        print(f"words.txt NOT found: {words_path}")
        TEST_RESULTS["tests"]["words.txt"] = {"exists": False}
    
    # Check sigmlFiles.json
    sigml_json_path = os.path.join(os.path.dirname(__file__), "recognition", "static", "recognition", "js", "sigmlFiles.json")
    print(f"\n{'='*60}")
    print("TEST: sigmlFiles.json Analysis")
    print('='*60)
    if os.path.exists(sigml_json_path):
        with open(sigml_json_path, 'r') as f:
            content = f.read()
        # This is a JS file, not pure JSON - it starts with "sigmlList = [...]"
        # Try to extract the array portion
        try:
            if 'sigmlList' in content:
                # Find the array part
                start = content.find('[')
                end = content.rfind(']')
                if start != -1 and end != -1:
                    json_data = json.loads(content[start:end+1])
                    entry_count = len(json_data)
                    print(f"sigmlFiles.json exists")
                    print(f"Entry count: {entry_count}")
                    print(f"First entry: {json_data[0] if json_data else 'None'}")
                    TEST_RESULTS["tests"]["sigmlFiles.json"] = {
                        "exists": True,
                        "entry_count": entry_count,
                        "sample_entry": json_data[0] if json_data else None
                    }
        except Exception as e:
            print(f"Error parsing sigmlFiles.json: {e}")
            TEST_RESULTS["tests"]["sigmlFiles.json"] = {
                "exists": True,
                "parse_error": str(e)
            }
    else:
        print(f"sigmlFiles.json NOT found: {sigml_json_path}")
        TEST_RESULTS["tests"]["sigmlFiles.json"] = {"exists": False}
    
    # Django collectstatic dry-run
    print(f"\n{'='*60}")
    print("TEST: Django collectstatic --dry-run")
    print('='*60)
    run_command("python manage.py collectstatic --dry-run --noinput 2>&1", "Collectstatic Dry Run")
    
    # Save results
    results_path = os.path.join(os.path.dirname(__file__), "test_results_part1.json")
    with open(results_path, 'w') as f:
        json.dump(TEST_RESULTS, f, indent=2)
    print(f"\n\nResults saved to: {results_path}")
    
    # Summary
    print("\n" + "#"*60)
    print("# PART 1 TEST SUMMARY")
    print("#"*60)
    total_tests = len(TEST_RESULTS["tests"])
    passed = sum(1 for t in TEST_RESULTS["tests"].values() if t.get("success", True))
    print(f"Total tests: {total_tests}")
    print(f"Passed/OK: {passed}")
    print(f"Failed: {total_tests - passed}")

if __name__ == "__main__":
    main()
