import json
import base64
import os
import sys
import argparse
import time
import requests

# Configuration
API_KEY = os.environ.get("RUNPOD_API_KEY")
if not API_KEY:
    print("Error: RUNPOD_API_KEY environment variable is not set.")
    sys.exit(1)

ENDPOINT_ID = "yo0g3z9woupofk"
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

def decode_and_save(data):
    """
    Traverses the data to find 'images' or 'videos' lists with base64 data and saves them.
    """
    
    # Check if we have the 'output' wrapper from RunPod (sync/async response structure)
    if isinstance(data, dict) and "output" in data:
        data = data["output"]

    if not isinstance(data, dict):
        print("Error: extracted content is not a dictionary.")
        return

    # Handle images
    images = data.get("images", [])
    if images:
        print(f"Found {len(images)} image(s).")
        for idx, img in enumerate(images):
            try:
                filename = img.get("filename", f"output_{idx}.png")
                img_type = img.get("type")
                img_data = img.get("data")

                if img_type == "base64" and img_data:
                    print(f"Decoding and saving {filename}...")
                    output_path = os.path.join(os.getcwd(), filename)
                    with open(output_path, "wb") as f:
                        f.write(base64.b64decode(img_data))
                    print(f"Saved to {output_path}")
                elif img_type == "s3_url":
                    print(f"Image {filename} is an S3 URL: {img.get('data')}")
                else:
                    print(f"Skipping image {filename}: unknown type or no data")
            except Exception as e:
                print(f"Error processing image {idx}: {e}")
    else:
        print("No 'images' found in the output.")

    # Handle videos
    videos = data.get("videos", [])
    if videos:
        print(f"Found {len(videos)} video(s).")
        for idx, vid in enumerate(videos):
            try:
                filename = vid.get("filename", f"output_{idx}.mp4")
                vid_type = vid.get("type")
                vid_data = vid.get("data")

                if vid_type == "base64" and vid_data:
                    print(f"Decoding and saving {filename}...")
                    output_path = os.path.join(os.getcwd(), filename)
                    with open(output_path, "wb") as f:
                        f.write(base64.b64decode(vid_data))
                    print(f"Saved to {output_path}")
                elif vid_type == "s3_url":
                    print(f"Video {filename} is an S3 URL: {vid.get('data')}")
                else:
                    print(f"Skipping video {filename}: unknown type or no data")
            except Exception as e:
                print(f"Error processing video {idx}: {e}")

import random

def run_job(input_file, prompt=None):
    print(f"Reading workflow from {input_file}...")
    with open(input_file, "r") as f:
        input_payload = json.load(f)

    # Validate structure
    workflow = input_payload.get("input", {}).get("workflow", {})
    if not workflow:
        print("Warning: Could not find 'input.workflow' in JSON. Modifications might fail.")
    else:
        # 1. Randomize Seed in KSampler
        for node_id, node in workflow.items():
            if node.get("class_type") == "KSampler":
                if "inputs" in node and "seed" in node["inputs"]:
                    new_seed = random.randint(1, 10**15)
                    node["inputs"]["seed"] = new_seed
                    print(f"Randomized seed for Node {node_id} to: {new_seed}")

        # 2. Update Prompt
        if prompt:
            prompt_updated = False
            for node_id, node in workflow.items():
                node_type = node.get("class_type")
                meta = node.get("_meta", {})
                title = meta.get("title", "").lower()
                
                # Logic for CLIPTextEncode
                if node_type == "CLIPTextEncode":
                    # Skip negative prompts
                    if "negative" in title:
                        continue
                    
                    # Update positive/generic prompts
                    if "inputs" in node and "text" in node["inputs"]:
                        node["inputs"]["text"] = prompt
                        print(f"Updated prompt for Node {node_id} ('{title}')")
                        prompt_updated = True

                # Logic for PrimitiveStringMultiline (often used as prompt widget)
                elif node_type == "PrimitiveStringMultiline":
                     # Skip negative primitives if properly labeled (unlikely but safe)
                    if "negative" in title:
                        continue
                        
                    if "prompt" in title or "positive" in title:
                        if "inputs" in node and "value" in node["inputs"]:
                            node["inputs"]["value"] = prompt
                            print(f"Updated prompt for Node {node_id} ('{title}')")
                            prompt_updated = True

            if not prompt_updated:
                 print("Warning: No suitable node found to update with the prompt.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 1. Submit Request
    print(f"Submitting job to {BASE_URL}/run ...")
    try:
        response = requests.post(f"{BASE_URL}/run", headers=headers, json=input_payload)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        print(f"Error submitting job: {e}")
        return

    job_id = result.get("id")
    status = result.get("status")
    print(f"Job submitted. ID: {job_id}, Status: {status}")

    # 2. Poll for completion
    while status in ["IN_QUEUE", "IN_PROGRESS"]:
        time.sleep(2)  # Wait a bit before polling
        try:
            r = requests.get(f"{BASE_URL}/status/{job_id}", headers=headers)
            r.raise_for_status()
            status_data = r.json()
            status = status_data.get("status")
            print(f"Status: {status}")
            
            if status == "COMPLETED":
                print("Job completed!")
                decode_and_save(status_data)
                return
            elif status == "FAILED":
                print("Job failed.")
                print(json.dumps(status_data, indent=2))
                return
        except Exception as e:
            print(f"Error polling status: {e}")
            time.sleep(5) # Backoff on error

def main():
    parser = argparse.ArgumentParser(description="Run RunPod job and decode output.")
    parser.add_argument("input_file", help="Path to JSON input file.")
    parser.add_argument("--prompt", help="Override the text prompt in the workflow.")
    args = parser.parse_args()

    run_job(args.input_file, args.prompt)

if __name__ == "__main__":
    main()
