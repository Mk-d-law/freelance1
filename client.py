import requests
import sseclient
import json
import re
import xml.etree.ElementTree as ET

def extract_memo_sections(xml_text):
    sections = {
        "issues": "",
        "discussion": "",
        "conclusion": ""
    }

    try:
        # Clean and parse XML
        cleaned = re.sub(r'```xml|```', '', xml_text).strip()
        root = ET.fromstring(cleaned)

        sections["issues"] = clean_section(root.findtext("issues_involved", ""))
        sections["discussion"] = clean_section(root.findtext("discussion_reasoning", ""))
        sections["conclusion"] = clean_section(root.findtext("findings_conclusion", ""))
    except ET.ParseError as e:
        print("XML parsing failed, falling back to regex:", e)
        # Fallback regex extraction
        def extract_tag_content(tag):
            match = re.search(f'<{tag}>(.*?)</{tag}>', xml_text, re.DOTALL)
            return clean_section(match.group(1)) if match else ""

        sections["issues"] = extract_tag_content("issues_involved")
        sections["discussion"] = extract_tag_content("discussion_reasoning")
        sections["conclusion"] = extract_tag_content("findings_conclusion")

    return sections


def clean_section(text):
    text = re.sub(r'\s+', ' ', text)  # collapse whitespace
    return text.strip()

def main():
    url = 'https://web-production-d52a.up.railway.app/process_dispute_sse'
    data = {
        "dispute": "arbitration"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }

    output = {
        "memo_json": {
            "issues": "",
            "discussion": "",
            "conclusion": ""
        },
        "initial_research": [],
        "conversation": []
    }

    with requests.post(url, json=data, headers=headers, stream=True) as response:
        client = sseclient.SSEClient(response)
        print("\n--- Streaming Events ---\n")

        for event in client.events():
            print(f"Event: {event.event}")
            print(f"Data: {event.data[:300]}...\n")  # Show only first 300 chars

            if event.event == "full_memo":
                try:
                    memo_data = json.loads(event.data)
                    xml_text = memo_data.get("text", "")
                    output["memo_json"] = extract_memo_sections(xml_text)
                except Exception as e:
                    print("Failed to parse full_memo:", e)

            elif event.event == "relevant_cases":
                try:
                    output["initial_research"] = json.loads(event.data)
                except Exception as e:
                    print("Failed to parse relevant_cases:", e)

            elif event.event == "conversation":
                try:
                    output["conversation"] = json.loads(event.data)
                except Exception as e:
                    print("Failed to parse conversation:", e)

            elif event.event == "done":
                print("Streaming complete.")
                break

    print("\n--- Final Structured JSON Output ---")
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
