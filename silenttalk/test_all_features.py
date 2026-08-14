"""
SilentTalk - Comprehensive End-to-End Test Suite
Tests: Auth (register/login/logout/profile), Learn progress, Nav, APIs, Models
"""
import os, sys, json, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "silenttalk.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from users.models import UserProfile
from learn.models import LetterProgress, LearningSession

RESULTS = []

def log(tid, name, ok, detail=""):
    RESULTS.append((tid, name, ok, detail))
    tag = "PASS" if ok else "FAIL"
    msg = f"  [{tag}] T{tid:02d} {name}"
    if detail:
        msg += f" -- {detail}"
    print(msg)

def run():
    print("=" * 70)
    print("  SilentTalk -- End-to-End Test Suite (Rebuilt)")
    print("=" * 70)

    # Cleanup old test users
    User.objects.filter(email="test@silenttalk.com").delete()
    User.objects.filter(email="dup@silenttalk.com").delete()

    c = Client()  # anonymous client

    # === SECTION 1: PAGE RENDERING ===
    print("\n-- Section 1: Page Rendering (Anonymous) --")
    pages = [
        (1, "/", "Landing"),
        (2, "/recognize/", "Recognize"),
        (3, "/text-to-isl/", "Text-to-ISL"),
        (4, "/gesture/", "Gesture"),
        (5, "/learn/", "Learn ISL"),
        (6, "/login/", "Login"),
        (7, "/register/", "Register"),
    ]
    for tid, url, name in pages:
        r = c.get(url)
        log(tid, f"{name} page loads", r.status_code == 200, f"HTTP {r.status_code}")

    # T08: Landing has Login button for anon
    r = c.get("/")
    log(8, "Landing shows Login button (anon)", b"Login" in r.content)

    # === SECTION 2: REGISTRATION ===
    print("\n-- Section 2: User Registration --")

    # T09: Successful registration
    r = c.post("/register/", {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@silenttalk.com",
        "password1": "securepass123",
        "password2": "securepass123",
    })
    log(9, "Registration redirects (302)", r.status_code == 302, f"HTTP {r.status_code}")

    # T10: User created in DB
    exists = User.objects.filter(email="test@silenttalk.com").exists()
    log(10, "User created in database", exists)

    # T11: UserProfile auto-created
    if exists:
        user = User.objects.get(email="test@silenttalk.com")
        has_prof = UserProfile.objects.filter(user=user).exists()
        log(11, "UserProfile auto-created", has_prof)
        if has_prof:
            prof = UserProfile.objects.get(user=user)
            log(12, "Avatar initials correct", prof.avatar_initial == "TU",
                f"Got '{prof.avatar_initial}'")
        else:
            log(12, "Avatar initials correct", False)
    else:
        log(11, "UserProfile auto-created", False)
        log(12, "Avatar initials correct", False)

    # T13: Auto-login after registration
    r = c.get("/")
    content = r.content.decode()
    log(13, "Auto-login after registration", "Test" in content,
        "Nav shows 'Test'" if "Test" in content else "Nav missing user name")

    # Logout
    c.get("/users/logout/")

    # T14: Duplicate email
    c2 = Client()
    r = c2.post("/register/", {
        "first_name": "Dup", "last_name": "User",
        "email": "test@silenttalk.com",
        "password1": "anotherpass1", "password2": "anotherpass1",
    })
    log(14, "Duplicate email rejected (stays 200)", r.status_code == 200, f"HTTP {r.status_code}")
    log(15, "Duplicate email error shown", b"already exists" in r.content)

    # T16: Password mismatch
    r = c2.post("/register/", {
        "first_name": "Mis", "last_name": "Match",
        "email": "dup@silenttalk.com",
        "password1": "passA12345", "password2": "passB12345",
    })
    log(16, "Password mismatch rejected", r.status_code == 200)
    log(17, "Password mismatch error shown", b"do not match" in r.content)

    # T18: Short password
    r = c2.post("/register/", {
        "first_name": "Short", "last_name": "Pw",
        "email": "dup@silenttalk.com",
        "password1": "abc", "password2": "abc",
    })
    log(18, "Short password rejected", b"at least 8" in r.content)

    # T19: Missing fields
    r = c2.post("/register/", {
        "first_name": "", "last_name": "",
        "email": "", "password1": "", "password2": "",
    })
    log(19, "Empty fields rejected", b"required" in r.content)

    # === SECTION 3: LOGIN ===
    print("\n-- Section 3: User Login --")

    c3 = Client()

    # T20: Login with correct credentials
    r = c3.post("/login/", {"email": "test@silenttalk.com", "password": "securepass123"})
    log(20, "Login succeeds (302)", r.status_code == 302, f"HTTP {r.status_code}")

    # T21: Landing shows user name
    r = c3.get("/")
    log(21, "Landing shows user name after login", b"Test" in r.content)

    # T22: Wrong password
    c4 = Client()
    r = c4.post("/login/", {"email": "test@silenttalk.com", "password": "wrongpass"})
    log(22, "Wrong password rejected (200)", r.status_code == 200)
    log(23, "Wrong password error shown", b"Invalid email or password" in r.content)

    # T24: Non-existent email
    r = c4.post("/login/", {"email": "nobody@nowhere.com", "password": "x"})
    log(24, "Unknown email rejected", b"Invalid email or password" in r.content)

    # T25: Empty login
    r = c4.post("/login/", {"email": "", "password": ""})
    log(25, "Empty login shows error", b"enter both" in r.content)

    # T26: Already-logged-in user goes to login -> redirect
    r = c3.get("/login/")
    log(26, "Logged-in user redirected from /login/", r.status_code == 302,
        f"HTTP {r.status_code}, Location: {r.get('Location', 'N/A')}")

    # T27: Already-logged-in user goes to register -> redirect
    r = c3.get("/register/")
    log(27, "Logged-in user redirected from /register/", r.status_code == 302)

    # === SECTION 4: PROFILE ===
    print("\n-- Section 4: User Profile --")

    # T28: Profile page loads (authenticated)
    r = c3.get("/users/profile/")
    log(28, "Profile loads (authenticated)", r.status_code == 200, f"HTTP {r.status_code}")

    # T29-31: Profile shows correct data
    content = r.content.decode()
    log(29, "Profile shows first+last name", "Test" in content and "User" in content)
    log(30, "Profile shows email", "test@silenttalk.com" in content)
    log(31, "Profile shows default role (Learner)", "Learner" in content)

    # T32: Profile has edit form fields
    log(32, "Profile has edit form fields",
        'name="first_name"' in content and 'name="bio"' in content and 'name="role"' in content)

    # T33: Profile edit works
    r = c3.post("/users/profile/", {
        "first_name": "Updated",
        "last_name": "Name",
        "email": "test@silenttalk.com",
        "bio": "I love ISL!",
        "role": "educator",
    })
    log(33, "Profile edit redirects (302)", r.status_code == 302)

    # T34: Verify changes persisted
    r = c3.get("/users/profile/")
    content = r.content.decode()
    log(34, "Bio saved and displayed", "I love ISL!" in content)
    log(35, "Role updated to Educator", "Educator" in content)
    log(36, "First name updated", "Updated" in content)

    # T37: Avatar initials recalculated
    user.refresh_from_db()
    prof = UserProfile.objects.get(user=user)
    log(37, "Avatar initials recalculated after edit", prof.avatar_initial == "UN",
        f"Got '{prof.avatar_initial}'")

    # T38: Profile blocked for anon
    c_anon = Client()
    r = c_anon.get("/users/profile/", follow=False)
    log(38, "Profile blocked for anon (302)", r.status_code == 302,
        f"Location: {r.get('Location', 'N/A')}")

    # T39: Redirect includes ?next=
    loc = r.get("Location", "")
    log(39, "Redirect has ?next=/users/profile/", "next=" in loc and "profile" in loc)

    # === SECTION 5: LOGOUT ===
    print("\n-- Section 5: Logout --")
    r = c3.get("/users/logout/", follow=False)
    log(40, "Logout redirects (302)", r.status_code == 302)

    r = c3.get("/")
    content = r.content.decode()
    log(41, "Landing shows Login after logout",
        "Login" in content and "Updated" not in content)

    # === SECTION 6: AUTH NAV ON ALL PAGES ===
    print("\n-- Section 6: Auth-Aware Nav on All Pages --")

    c5 = Client()
    c5.post("/login/", {"email": "test@silenttalk.com", "password": "securepass123"})

    nav_pages = [
        ("/", "Landing"),
        ("/recognize/", "Recognize"),
        ("/text-to-isl/", "Text-to-ISL"),
        ("/gesture/", "Gesture"),
        ("/learn/", "Learn ISL"),
    ]
    tid = 42
    for url, name in nav_pages:
        r = c5.get(url)
        content = r.content.decode()
        has_name = "Updated" in content
        has_logout = "logout" in content.lower()
        log(tid, f"{name} shows user name (auth)", has_name,
            f"logout={has_logout}")
        tid += 1

    c_anon3 = Client()
    for url, name in nav_pages:
        r = c_anon3.get(url)
        content = r.content.decode()
        has_login = "Login" in content
        no_name = "Updated" not in content
        log(tid, f"{name} shows Login btn (anon)", has_login and no_name)
        tid += 1

    # === SECTION 7: LEARN PROGRESS ===
    print("\n-- Section 7: Learn App Progress Tracking --")

    # T52: Learn page has auth flag
    r = c5.get("/learn/")
    log(tid, "Learn page has IS_AUTHENTICATED var",
        b"IS_AUTHENTICATED" in r.content or b"is_authenticated" in r.content)
    tid += 1

    # T53: Save progress API
    r = c5.post("/learn/api/save-progress/",
        data=json.dumps({"mastered": ["A","B","C"], "guided": ["A","B","C","D","E"]}),
        content_type="application/json")
    log(tid, "Save progress API (200)", r.status_code == 200, f"HTTP {r.status_code}")
    tid += 1

    rd = r.json()
    log(tid, "Save returns correct counts",
        rd.get("mastered") == 3 and rd.get("guided") == 5,
        f"m={rd.get('mastered')}, g={rd.get('guided')}")
    tid += 1

    # T55: DB check
    user = User.objects.get(email="test@silenttalk.com")
    mc = LetterProgress.objects.filter(user=user, status="mastered").count()
    gc = LetterProgress.objects.filter(user=user, status="guided").count()
    log(tid, "Progress persisted in DB", mc == 3 and gc == 2,
        f"mastered={mc}, guided_only={gc}")
    tid += 1

    # T56: Load progress
    r = c5.get("/learn/api/load-progress/")
    log(tid, "Load progress API (200)", r.status_code == 200)
    tid += 1

    rd = r.json()
    log(tid, "Load returns correct mastered",
        set(rd.get("mastered", [])) == {"A","B","C"},
        f"{rd.get('mastered')}")
    tid += 1

    log(tid, "Load returns correct guided",
        set(rd.get("guided", [])) == {"A","B","C","D","E"},
        f"{rd.get('guided')}")
    tid += 1

    # T59: Save blocked for anon
    r = c_anon3.post("/learn/api/save-progress/",
        data=json.dumps({"mastered": ["X"]}),
        content_type="application/json")
    log(tid, "Save progress blocked for anon (401)", r.status_code == 401)
    tid += 1

    # T60: Load returns empty for anon
    r = c_anon3.get("/learn/api/load-progress/")
    rd = r.json()
    log(tid, "Load progress empty for anon",
        rd.get("mastered") == [] and rd.get("guided") == [])
    tid += 1

    # T61: UserProfile stats updated
    prof = UserProfile.objects.get(user=user)
    log(tid, "Profile total_signs_practiced updated",
        prof.total_signs_practiced == 8,
        f"Got {prof.total_signs_practiced}")
    tid += 1

    # === SECTION 8: EXISTING APIs ===
    print("\n-- Section 8: Existing API Endpoints --")

    r = c.post("/process-text/", {"text": "Hello how are you"})
    log(tid, "Process Text API (200)", r.status_code == 200)
    tid += 1
    rd = r.json()
    log(tid, "Process Text returns tokens",
        "tokens" in rd and len(rd["tokens"]) > 0, f"{rd.get('tokens')}")
    tid += 1

    r = c.post("/predict/", {})
    log(tid, "Predict API handles missing frame (200)", r.status_code == 200)
    tid += 1
    rd = r.json()
    log(tid, "Predict returns error msg", rd.get("letter") == "" and "error" in rd)
    tid += 1

    r = c.post("/predict-gesture/", {})
    log(tid, "Predict Gesture handles missing frame", r.status_code == 200)
    tid += 1

    # === SECTION 9: ADMIN ===
    print("\n-- Section 9: Admin Registration --")

    from django.contrib.admin.sites import site
    log(tid, "UserProfile in admin", UserProfile in site._registry)
    tid += 1
    log(tid, "LetterProgress in admin", LetterProgress in site._registry)
    tid += 1
    log(tid, "LearningSession in admin", LearningSession in site._registry)
    tid += 1

    # === SECTION 10: MODELS ===
    print("\n-- Section 10: Database Models --")

    prof = UserProfile.objects.get(user=user)
    log(tid, "UserProfile has role", hasattr(prof, "role"), f"role={prof.role}")
    tid += 1
    log(tid, "UserProfile has bio", hasattr(prof, "bio"), f"bio={prof.bio}")
    tid += 1
    log(tid, "UserProfile has avatar_initial", hasattr(prof, "avatar_initial"))
    tid += 1
    log(tid, "UserProfile has stats fields",
        all(hasattr(prof, f) for f in ["total_signs_practiced","total_conversations","total_translations"]))
    tid += 1

    lp = LetterProgress.objects.filter(user=user).first()
    log(tid, "LetterProgress works", lp is not None,
        f"letter={lp.letter}, status={lp.status}" if lp else "")
    tid += 1

    from django.db import IntegrityError
    try:
        LetterProgress.objects.create(user=user, letter="A")
        log(tid, "LetterProgress unique constraint", False, "DUPLICATE ALLOWED!")
    except IntegrityError:
        log(tid, "LetterProgress unique constraint enforced", True)
    tid += 1

    # === CLEANUP ===
    User.objects.filter(email="test@silenttalk.com").delete()
    User.objects.filter(email="dup@silenttalk.com").delete()

    # === SUMMARY ===
    total = len(RESULTS)
    passed = sum(1 for _,_,s,_ in RESULTS if s)
    failed = total - passed
    print("\n" + "=" * 70)
    print(f"  TOTAL: {total} | PASSED: {passed} | FAILED: {failed}")
    print(f"  Pass Rate: {passed/total*100:.1f}%")
    print("=" * 70)

    if failed > 0:
        print("\n  FAILED TESTS:")
        for t, n, s, d in RESULTS:
            if not s:
                print(f"    T{t:02d} {n} -- {d}")

    with open("test_results.json", "w") as f:
        json.dump([{"id":t,"name":n,"passed":s,"detail":d} for t,n,s,d in RESULTS], f, indent=2)
    print("\n  Results saved to test_results.json")

if __name__ == "__main__":
    run()
