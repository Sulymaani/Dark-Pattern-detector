"""
Quick script to test the /detect endpoint with a screenshot.
Usage: python test_screenshot.py <path_to_screenshot>
"""

import sys
import httpx


def test_screenshot(image_path: str):
    url = "http://127.0.0.1:8000/detect"

    with open(image_path, "rb") as f:
        files = {"file": (image_path, f, "image/png")}
        response = httpx.post(url, files=files, timeout=60.0)

    print(f"Status: {response.status_code}")
    print(f"Response:\n{response.json()}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n--- Results ---")
        print(f"Text extracted: {len(data['extracted_text'])} characters")
        print(f"Patterns found: {len(data['patterns'])}")

        for p in data["patterns"]:
            print(
                f"\n  • {p['pattern_type'].upper()} (confidence: {p['confidence']:.0%})"
            )
            print(f"    Evidence: {p['evidence'][:100]}...")
            print(f"    Reason: {p['explanation']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_screenshot.py <path_to_screenshot>")
        sys.exit(1)

    test_screenshot(sys.argv[1])
