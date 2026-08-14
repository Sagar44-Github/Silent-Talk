#!/usr/bin/env python3
"""
Silent Talk Comprehensive Test Suite
Runs all test parts and generates the final report.
"""

import subprocess
import sys
import os
import json
import time
import base64
import numpy as np
from datetime import datetime

# Use the correct Python from silenttalk_env
PYTHON_EXE = r'd:\Semester - 4\Full Stack Development\SilentTalk - The Project\silenttalk_env\Scripts\python.exe'
PROJECT_DIR = r'd:\Semester - 4\Full Stack Development\SilentTalk - The Project\silenttalk'

os.chdir(PROJECT_DIR)
sys.path.insert(0, PROJECT_DIR)

# Test results storage
ALL_RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "python_version": sys.version,
    "platform": sys.platform,
    "parts": {}
}

def log_section(title):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def run_with_venv(cmd, description, timeout=60):
    """Run command using the venv Python."""
    print(f"\n--- {description} ---")
    print(f"Command: {cmd}")
    try:
        # Replace 'python ' with the full path to venv python
        if cmd.startswith('python '):
            cmd = f'"{PYTHON_EXE}" ' + cmd[7:]
        elif cmd.startswith('pip '):
            pip_path = PYTHON_EXE.replace('python.exe', 'pip.exe')
            cmd = f'"{pip_path}" ' + cmd[4:]
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        print(f"Return code: {result.returncode}")
        if output:
            print(f"Output: {output[:500]}..." if len(output) > 500 else f"Output: {output}")
        if error and result.returncode != 0:
            print(f"Error: {error[:500]}..." if len(error) > 500 else f"Error: {error}")
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "output": output,
            "error": error if error else None
        }
    except Exception as e:
        print(f"Exception: {e}")
        return {"success": False, "error": str(e)}

def part1_environment():
    """Part 1: Environment and Dependency Testing"""
    log_section("PART 1: ENVIRONMENT AND DEPENDENCY TESTING")
    results = {"tests": {}}
    
    # Python and package versions
    tests = [
        ('python --version', 'Python Version'),
        ('python -m django --version', 'Django Version'),
        ('pip show mediapipe', 'MediaPipe Version'),
        ('pip show tensorflow', 'TensorFlow Version'),
        ('pip show opencv-python', 'OpenCV Version'),
        ('pip show scikit-learn', 'scikit-learn Version'),
        ('pip show numpy', 'NumPy Version'),
        ('pip freeze', 'All Installed Packages'),
        ('pip check', 'Dependency Conflict Check'),
    ]
    
    for cmd, desc in tests:
        results["tests"][desc] = run_with_venv(cmd, desc)
    
    # Virtual environment check
    results["tests"]["Virtual Environment Check"] = {
        "in_venv": hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix),
        "prefix": sys.prefix,
        "executable": sys.executable
    }
    
    # Model files
    model_p_path = os.path.join(PROJECT_DIR, 'recognition', 'model.p')
    gesture_model_path = os.path.join(PROJECT_DIR, 'recognition', 'static', 'recognition', 'gesture_recognizer.task')
    
    for path, name in [(model_p_path, 'model.p'), (gesture_model_path, 'gesture_recognizer.task')]:
        if os.path.exists(path):
            size = os.path.getsize(path)
            results["tests"][f"{name} File Check"] = {
                "exists": True, "size_bytes": size, "size_mb": round(size/1024/1024, 2)
            }
        else:
            results["tests"][f"{name} File Check"] = {"exists": False}
    
    # Test loading model.p
    print("\n--- Testing model.p loading ---")
    try:
        import pickle
        start = time.time()
        with open(model_p_path, 'rb') as f:
            model_dict = pickle.load(f)
        elapsed = (time.time() - start) * 1000
        results["tests"]["Load model.p"] = {
            "success": True, "load_time_ms": round(elapsed, 2),
            "model_type": str(type(model_dict.get('model'))),
            "dict_keys": list(model_dict.keys())
        }
        print(f"Model loaded successfully in {elapsed:.2f} ms")
    except Exception as e:
        import traceback
        results["tests"]["Load model.p"] = {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        print(f"Failed: {e}")
    
    # Test loading gesture recognizer
    print("\n--- Testing gesture_recognizer.task loading ---")
    try:
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        start = time.time()
        with open(gesture_model_path, "rb") as f:
            model_data = f.read()
        base_options = python.BaseOptions(model_asset_buffer=model_data)
        options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=2)
        recognizer = vision.GestureRecognizer.create_from_options(options)
        elapsed = (time.time() - start) * 1000
        results["tests"]["Load gesture_recognizer.task"] = {
            "success": True, "load_time_ms": round(elapsed, 2)
        }
        print(f"Gesture recognizer loaded in {elapsed:.2f} ms")
    except Exception as e:
        import traceback
        results["tests"]["Load gesture_recognizer.task"] = {"success": False, "error": str(e)}
        print(f"Failed: {e}")
    
    # Static files
    signfiles_dir = os.path.join(PROJECT_DIR, 'recognition', 'static', 'recognition', 'SignFiles')
    if os.path.exists(signfiles_dir):
        sigml_count = len([f for f in os.listdir(signfiles_dir) if f.endswith('.sigml')])
        results["tests"]["SIGML File Count"] = {"count": sigml_count, "directory": signfiles_dir}
        print(f"\nSIGML files: {sigml_count}")
    
    # words.txt
    words_path = os.path.join(PROJECT_DIR, 'recognition', 'static', 'recognition', 'words.txt')
    if os.path.exists(words_path):
        import re
        with open(words_path, 'r') as f:
            content = f.read()
        words = [w.strip().lower() for w in re.findall(r"'([^']+)'", content)]
        results["tests"]["words.txt"] = {"exists": True, "word_count": len(words), "sample": words[:10]}
        print(f"words.txt: {len(words)} words")
    
    # sigmlFiles.json
    sigml_json_path = os.path.join(PROJECT_DIR, 'recognition', 'static', 'recognition', 'js', 'sigmlFiles.json')
    if os.path.exists(sigml_json_path):
        with open(sigml_json_path, 'r') as f:
            content = f.read()
        try:
            start = content.find('[')
            end = content.rfind(']')
            if start != -1 and end != -1:
                json_data = json.loads(content[start:end+1])
                results["tests"]["sigmlFiles.json"] = {"exists": True, "entry_count": len(json_data)}
                print(f"sigmlFiles.json: {len(json_data)} entries")
        except Exception as e:
            results["tests"]["sigmlFiles.json"] = {"exists": True, "parse_error": str(e)}
    
    # Django checks
    results["tests"]["Django check"] = run_with_venv('python manage.py check', 'Django System Check')
    results["tests"]["Show migrations"] = run_with_venv('python manage.py showmigrations', 'Migration Status')
    
    ALL_RESULTS["parts"]["Part 1"] = results
    return results

def part2_django_server():
    """Part 2: Django Server and URL Testing"""
    log_section("PART 2: DJANGO SERVER AND URL TESTING")
    results = {"tests": {}, "urls": {}}
    
    # Start Django server in background
    print("\n--- Starting Django development server ---")
    server_process = subprocess.Popen(
        [PYTHON_EXE, 'manage.py', 'runserver', '127.0.0.1:8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=PROJECT_DIR
    )
    
    # Wait for server to start
    time.sleep(5)
    
    import requests
    
    # Test URLs
    base_url = 'http://127.0.0.1:8000'
    urls_to_test = [
        ('GET', '/', 'Landing Page'),
        ('GET', '/recognize/', 'Letter Recognition Page'),
        ('GET', '/gesture/', 'Gesture Recognition Page'),
        ('GET', '/text-to-isl/', 'Text to ISL Page'),
        ('GET', '/learn/', 'Learn ISL Page'),
        ('GET', '/login/', 'Login Page'),
        ('GET', '/register/', 'Register Page'),
        ('GET', '/predict/', 'Predict API (GET - should be 405)'),
        ('GET', '/predict-gesture/', 'Predict Gesture API (GET - should be 405)'),
        ('GET', '/process-text/', 'Process Text API (GET - should be 405)'),
        ('GET', '/nonexistent-page/', 'Nonexistent Page (should be 404)'),
    ]
    
    for method, path, desc in urls_to_test:
        url = base_url + path
        try:
            start = time.time()
            if method == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, timeout=10)
            elapsed = (time.time() - start) * 1000
            
            results["urls"][desc] = {
                "status_code": response.status_code,
                "response_time_ms": round(elapsed, 2),
                "content_type": response.headers.get('Content-Type', 'unknown'),
                "content_length": len(response.content),
                "success": response.status_code < 400 or '405' in desc or '404' in desc
            }
            print(f"{desc}: {response.status_code} in {elapsed:.2f} ms")
        except Exception as e:
            results["urls"][desc] = {"error": str(e), "success": False}
            print(f"{desc}: ERROR - {e}")
    
    # Stop server
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except:
        server_process.kill()
    
    ALL_RESULTS["parts"]["Part 2"] = results
    return results

def part3_ai_engine():
    """Part 3: AI Engine Unit Testing"""
    log_section("PART 3: AI ENGINE UNIT TESTING")
    results = {"tests": {}}
    
    # Import AI engine
    try:
        sys.path.insert(0, os.path.join(PROJECT_DIR, 'recognition'))
        from ai_engine import predict_from_frame, detect_emotion, labels_dict
        print("AI engine imported successfully")
    except Exception as e:
        print(f"Failed to import AI engine: {e}")
        results["tests"]["Import Error"] = {"error": str(e)}
        ALL_RESULTS["parts"]["Part 3"] = results
        return results
    
    # Test 3.1.5: Verify 38 classes
    print("\n--- Test 3.1.5: Class Label Verification ---")
    expected_classes = 38
    actual_classes = len(labels_dict)
    print(f"Expected classes: {expected_classes}")
    print(f"Actual classes: {actual_classes}")
    print(f"Labels: {labels_dict}")
    results["tests"]["Class Count"] = {
        "expected": expected_classes,
        "actual": actual_classes,
        "labels": labels_dict,
        "success": actual_classes == expected_classes
    }
    
    # Test 3.1.4: Edge case frames
    print("\n--- Test 3.1.4: Edge Case Frames ---")
    edge_cases = [
        ("Black frame", np.zeros((480, 640, 3), dtype=np.uint8)),
        ("White frame", np.full((480, 640, 3), 255, dtype=np.uint8)),
        ("Random noise", np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)),
        ("Small frame 50x50", np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)),
        ("Large frame 1920x1080", np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)),
    ]
    
    for name, frame in edge_cases:
        try:
            start = time.time()
            result = predict_from_frame(frame)
            elapsed = (time.time() - start) * 1000
            results["tests"][f"Edge case: {name}"] = {
                "result": result,
                "time_ms": round(elapsed, 2),
                "exception": None
            }
            print(f"{name}: {result} ({elapsed:.2f} ms)")
        except Exception as e:
            results["tests"][f"Edge case: {name}"] = {"result": None, "exception": str(e)}
            print(f"{name}: EXCEPTION - {e}")
    
    # Test 3.1.5: detect_emotion with no face
    print("\n--- Test 3.3.2: Emotion detection with no face ---")
    gray_frame = np.full((480, 640, 3), 128, dtype=np.uint8)
    try:
        start = time.time()
        emotion, face_detected = detect_emotion(gray_frame)
        elapsed = (time.time() - start) * 1000
        results["tests"]["Emotion - no face"] = {
            "emotion": emotion,
            "face_detected": face_detected,
            "time_ms": round(elapsed, 2)
        }
        print(f"No face: emotion={emotion}, detected={face_detected} ({elapsed:.2f} ms)")
    except Exception as e:
        results["tests"]["Emotion - no face"] = {"error": str(e)}
        print(f"No face: EXCEPTION - {e}")
    
    # Test 3.4: Performance - 100 predictions
    print("\n--- Test 3.4: Performance (100 predictions) ---")
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    times = []
    for _ in range(100):
        start = time.time()
        predict_from_frame(test_frame)
        times.append((time.time() - start) * 1000)
    
    import statistics
    perf_stats = {
        "min_ms": round(min(times), 2),
        "max_ms": round(max(times), 2),
        "mean_ms": round(statistics.mean(times), 2),
        "median_ms": round(statistics.median(times), 2),
        "std_dev_ms": round(statistics.stdev(times), 2) if len(times) > 1 else 0
    }
    results["tests"]["Performance 100 runs"] = perf_stats
    print(f"Performance: {perf_stats}")
    
    ALL_RESULTS["parts"]["Part 3"] = results
    return results

def part4_gesture_engine():
    """Part 4: Gesture Engine Unit Testing"""
    log_section("PART 4: GESTURE ENGINE UNIT TESTING")
    results = {"tests": {}}
    
    try:
        sys.path.insert(0, os.path.join(PROJECT_DIR, 'recognition'))
        from gesture_engine import recognize_gesture
        print("Gesture engine imported successfully")
    except Exception as e:
        print(f"Failed to import gesture engine: {e}")
        results["tests"]["Import Error"] = {"error": str(e)}
        ALL_RESULTS["parts"]["Part 4"] = results
        return results
    
    # Test with no hand (plain frame)
    print("\n--- Test 4.2.2: Frame with no hand ---")
    plain_frame = np.full((480, 640, 3), 128, dtype=np.uint8)
    try:
        start = time.time()
        name, display, confidence = recognize_gesture(plain_frame)
        elapsed = (time.time() - start) * 1000
        results["tests"]["No hand frame"] = {
            "name": name,
            "display": display,
            "confidence": confidence,
            "time_ms": round(elapsed, 2)
        }
        print(f"No hand: name={name}, display={display}, conf={confidence} ({elapsed:.2f} ms)")
    except Exception as e:
        results["tests"]["No hand frame"] = {"error": str(e)}
        print(f"No hand: EXCEPTION - {e}")
    
    # Performance test
    print("\n--- Test 4.2.5: Performance (100 runs) ---")
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    times = []
    for _ in range(100):
        start = time.time()
        recognize_gesture(test_frame)
        times.append((time.time() - start) * 1000)
    
    import statistics
    perf_stats = {
        "min_ms": round(min(times), 2),
        "max_ms": round(max(times), 2),
        "mean_ms": round(statistics.mean(times), 2),
        "median_ms": round(statistics.median(times), 2),
        "std_dev_ms": round(statistics.stdev(times), 2) if len(times) > 1 else 0
    }
    results["tests"]["Performance 100 runs"] = perf_stats
    print(f"Performance: {perf_stats}")
    
    ALL_RESULTS["parts"]["Part 4"] = results
    return results

def part5_api_endpoints():
    """Part 5: API Endpoint Integration Testing"""
    log_section("PART 5: API ENDPOINT INTEGRATION TESTING")
    results = {"tests": {}}
    
    # Start server
    print("\n--- Starting Django server ---")
    server_process = subprocess.Popen(
        [PYTHON_EXE, 'manage.py', 'runserver', '127.0.0.1:8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=PROJECT_DIR
    )
    time.sleep(5)
    
    try:
        import requests
        base_url = 'http://127.0.0.1:8000'
        
        # Test /predict/ with valid frame (base64 encoded empty image)
        print("\n--- Test 5.1.4: Malformed inputs to /predict/ ---")
        
        # Missing frame
        response = requests.post(f'{base_url}/predict/', data={}, timeout=10)
        results["tests"]["POST /predict/ - no frame"] = {
            "status": response.status_code,
            "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text[:200]
        }
        print(f"No frame: {response.status_code}")
        
        # Empty frame
        response = requests.post(f'{base_url}/predict/', data={'frame': ''}, timeout=10)
        results["tests"]["POST /predict/ - empty frame"] = {
            "status": response.status_code,
            "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text[:200]
        }
        print(f"Empty frame: {response.status_code}")
        
        # Invalid base64
        response = requests.post(f'{base_url}/predict/', data={'frame': 'data:image/jpeg;base64,invalid!!!'}, timeout=10)
        results["tests"]["POST /predict/ - invalid base64"] = {
            "status": response.status_code,
            "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text[:200]
        }
        print(f"Invalid base64: {response.status_code}")
        
        # Test /process-text/
        print("\n--- Test 5.3: /process-text/ endpoint ---")
        test_cases = [
            ('hello', 'Known word'),
            ('thank you', 'Multiple known words'),
            ('Sagar', 'Unknown word (fingerspell)'),
            ('hello Sagar', 'Mixed input'),
            ('', 'Empty string'),
            ('123', 'Numbers'),
            ('HELLO', 'All caps'),
        ]
        
        for text, desc in test_cases:
            response = requests.post(f'{base_url}/process-text/', data={'text': text}, timeout=10)
            try:
                json_resp = response.json()
                results["tests"][f"POST /process-text/ - {desc}"] = {
                    "status": response.status_code,
                    "tokens": json_resp.get('tokens', []),
                    "original": json_resp.get('original', '')
                }
                print(f"{desc}: {json_resp.get('tokens', [])}")
            except:
                results["tests"][f"POST /process-text/ - {desc}"] = {
                    "status": response.status_code,
                    "response": response.text[:200]
                }
                print(f"{desc}: Error parsing response")
        
    except Exception as e:
        print(f"API test error: {e}")
        results["tests"]["Error"] = {"message": str(e)}
    finally:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except:
            server_process.kill()
    
    ALL_RESULTS["parts"]["Part 5"] = results
    return results

def part12_code_quality():
    """Part 12: Code Quality Checks"""
    log_section("PART 12: CODE QUALITY CHECKS")
    results = {"tests": {}}
    
    files_to_check = [
        'recognition/ai_engine.py',
        'recognition/gesture_engine.py',
        'recognition/views.py',
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(PROJECT_DIR, file_path)
        print(f"\n--- Checking {file_path} ---")
        result = run_with_venv(f'python -m py_compile {file_path}', f'Syntax check {file_path}')
        results["tests"][f"Syntax check {file_path}"] = result
    
    # Django deployment check
    results["tests"]["Django deployment check"] = run_with_venv(
        'python manage.py check --deploy', 
        'Django Deployment Check',
        timeout=30
    )
    
    ALL_RESULTS["parts"]["Part 12"] = results
    return results

def generate_report():
    """Generate the final test report"""
    log_section("GENERATING FINAL TEST REPORT")
    
    # Save raw results
    results_path = os.path.join(PROJECT_DIR, 'SILENT_TALK_TEST_RESULTS.json')
    with open(results_path, 'w') as f:
        json.dump(ALL_RESULTS, f, indent=2)
    print(f"Raw results saved to: {results_path}")
    
    # Generate markdown report
    report_path = os.path.join(PROJECT_DIR, 'SILENT_TALK_TEST_REPORT.md')
    
    report_lines = [
        "# Silent Talk — Complete System Test Report",
        f"**Generated:** {ALL_RESULTS['timestamp']}",
        "**Tested by:** Automated Test Suite",
        f"**Python version:** {ALL_RESULTS['python_version'].split()[0]}",
        f"**Platform:** {ALL_RESULTS['platform']}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
    ]
    
    # Calculate overall stats
    total_tests = 0
    passed_tests = 0
    
    for part_name, part_data in ALL_RESULTS["parts"].items():
        if "tests" in part_data:
            for test_name, test_result in part_data["tests"].items():
                total_tests += 1
                if isinstance(test_result, dict) and test_result.get("success", True):
                    passed_tests += 1
    
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    report_lines.extend([
        f"This report covers comprehensive testing of the Silent Talk Django platform.",
        f"",
        f"**Overall Test Result:** {'PASS' if pass_rate > 80 else 'PARTIAL' if pass_rate > 50 else 'FAIL'}",
        f"",
        f"| Category | Tests Run | Passed | Failed | Pass Rate |",
        f"|---|---|---|---|---|",
    ])
    
    for part_name, part_data in ALL_RESULTS["parts"].items():
        if "tests" in part_data:
            part_total = len(part_data["tests"])
            part_passed = sum(1 for t in part_data["tests"].values() if isinstance(t, dict) and t.get("success", True))
            part_rate = round(part_passed / part_total * 100, 1) if part_total > 0 else 0
            report_lines.append(f"| {part_name} | {part_total} | {part_passed} | {part_total - part_passed} | {part_rate}% |")
    
    report_lines.extend([
        f"| **TOTAL** | {total_tests} | {passed_tests} | {total_tests - passed_tests} | {round(pass_rate, 1)}% |",
        "",
        "---",
        "",
    ])
    
    # Add detailed results for each part
    for part_name, part_data in ALL_RESULTS["parts"].items():
        report_lines.extend([
            f"## {part_name}",
            "",
            "```json",
            json.dumps(part_data, indent=2),
            "```",
            "",
        ])
    
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Report saved to: {report_path}")
    return report_path

def main():
    print("#"*70)
    print("# SILENT TALK COMPREHENSIVE TEST SUITE")
    print("#"*70)
    
    # Run all test parts
    try:
        part1_environment()
    except Exception as e:
        print(f"Part 1 error: {e}")
    
    try:
        part2_django_server()
    except Exception as e:
        print(f"Part 2 error: {e}")
    
    try:
        part3_ai_engine()
    except Exception as e:
        print(f"Part 3 error: {e}")
    
    try:
        part4_gesture_engine()
    except Exception as e:
        print(f"Part 4 error: {e}")
    
    try:
        part5_api_endpoints()
    except Exception as e:
        print(f"Part 5 error: {e}")
    
    try:
        part12_code_quality()
    except Exception as e:
        print(f"Part 12 error: {e}")
    
    # Generate final report
    report_path = generate_report()
    
    print("\n" + "="*70)
    print(" TESTING COMPLETE")
    print("="*70)
    print(f"Report location: {report_path}")

if __name__ == "__main__":
    main()
