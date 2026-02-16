import urllib.request
import urllib.parse
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_create_url():
    url = f"{BASE_URL}/api/urls"
    data = {"original_url": "https://www.google.com"}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                print(f"✅ Create URL success: {result['code']}")
                return result
            else:
                print(f"❌ Create URL failed: {response.status}")
    except Exception as e:
        print(f"❌ Create URL error: {e}")
    return None

def test_get_url(code):
    url = f"{BASE_URL}/api/urls/{code}"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                print(f"✅ Get URL success: {result['original_url']}")
            else:
                print(f"❌ Get URL failed: {response.status}")
    except Exception as e:
        print(f"❌ Get URL error: {e}")

def test_redirect(code):
    url = f"{BASE_URL}/{code}"
    try:
        # Prevent auto-redirect to check 307/302? urllib follows redirects by default.
        # However, we just want to see if it works (returns google.com content or 200 after redirect).
        # We can use a custom opener to stop redirect, but testing that it reaches google is fine too.
        # Actually google.com might be large.
        
        # Let's just check if we get a response.
        with urllib.request.urlopen(url) as response:
             print(f"✅ Redirect followed to: {response.geturl()}")
             # If response.geturl() starts with google.com, it worked.
             if "google.com" in response.geturl():
                 print("✅ Redirect target verified.")
             else:
                 print(f"⚠️ Redirect target mismatch: {response.geturl()}")
    except Exception as e:
        print(f"❌ Redirect error: {e}")

def main():
    print("Testing Backend...")
    # Wait for server to be ready
    for _ in range(5):
        try:
            with urllib.request.urlopen(BASE_URL) as response:
                if response.status == 200:
                    print("✅ Server is up.")
                    break
        except:
            print("Waiting for server...")
            time.sleep(1)
    
    created_url = test_create_url()
    if created_url:
        code = created_url['code']
        test_get_url(code)
        
        # Test Update
        print(f"\nTesting Update for {code}...")
        update_data = {"original_url": "https://www.google.com/updated"}
        req = urllib.request.Request(
            f"{BASE_URL}/api/urls/{code}", 
            data=json.dumps(update_data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    print(f"✅ Update URL success. New target: {result['original_url']}")
                    if result['original_url'] == "https://www.google.com/updated":
                        print("✅ Update verified.")
        except Exception as e:
            print(f"❌ Update URL error: {e}")

        # Test Custom Alias
        print("\nTesting Custom Alias...")
        alias = "myalias" + str(int(time.time()))
        alias_data = {"custom_alias": alias}
        req = urllib.request.Request(
            f"{BASE_URL}/api/urls/{code}", 
            data=json.dumps(alias_data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        try:
             with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    print(f"✅ Custom Alias success: {result['short_url']}")
                    code = alias # Update code for next tests
        except Exception as e:
            print(f"❌ Custom Alias error: {e}")

        test_redirect(code)
        
        # Test Delete
        print(f"\nTesting Delete for {code}...")
        req = urllib.request.Request(
            f"{BASE_URL}/api/urls/{code}", 
            method='DELETE'
        )
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("✅ Delete URL success.")
        except Exception as e:
            print(f"❌ Delete URL error: {e}")
            
        # Verify 404
        try:
            urllib.request.urlopen(f"{BASE_URL}/api/urls/{code}")
            print("❌ Error: URL should be deleted but returned 200")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("✅ Verify Delete (404) success.")
            else:
                print(f"❌ Verify Delete failed with code {e.code}")
        except Exception as e:
             print(f"❌ Verify Delete error: {e}")

if __name__ == "__main__":
    main()
