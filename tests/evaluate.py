import json, requests, sys

API_URL = "http://localhost:5000/generate"


def run_tests():
    with open("tests/tests.json", "r") as f:
        tests = json.load(f)

    passed = 0
    print(f"{'Mode':<6} | {'Topic':<15} | {'Result':<6} | {'Details'}")
    print("-" * 60)

    for t in tests:
        payload = {"topic": t["input"], "mode": t["mode"]}
        try:
            res = requests.post(API_URL, json=payload)

            if t.get("expect_error"):
                if res.status_code == 400:
                    print(f"{t['mode']:<6} | {t['input']:<15} | PASS   | Caught unsafe input")
                    passed += 1
                else:
                    print(f"{t['mode']:<6} | {t['input']:<15} | FAIL   | Should have failed")
                continue

            data = res.json().get("content")

            if t["type"] == "json":
                # Check if response is a dict and has keys
                if isinstance(data, dict) and all(k in data for k in t["must_contain_keys"]):
                    print(f"{t['mode']:<6} | {t['input']:<15} | PASS   | Valid JSON Schema")
                    passed += 1
                else:
                    print(f"{t['mode']:<6} | {t['input']:<15} | FAIL   | Invalid JSON")
            else:
                # Text check
                if all(k.lower() in str(data).lower() for k in t["must_contain"]):
                    print(f"{t['mode']:<6} | {t['input']:<15} | PASS   | Keywords found")
                    passed += 1
                else:
                    print(f"{t['mode']:<6} | {t['input']:<15} | FAIL   | Missing keywords")

        except Exception as e:
            print(f"{t['mode']:<6} | {t['input']:<15} | ERR    | {e}")

    print("-" * 60)
    success_rate = (passed / len(tests)) * 100
    print(f"Pass Rate: {success_rate}%")


if __name__ == "__main__":
    run_tests()