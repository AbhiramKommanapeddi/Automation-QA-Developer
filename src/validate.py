import os
import json

def run_validation():
    base_dir = "c:\\Users\\abhik\\Downloads\\Automation & QA Developer"
    files_to_check = [
        ("Task1_QA_Report_Abhik.pdf", "binary"),
        ("Task2_Workflow_Abhik.json", "json"),
        ("Bonus_UptimeMonitor_Abhik.json", "json"),
        ("README.md", "text"),
        ("src/generate_pdf.py", "text")
    ]
    
    print("=== STARTING QA DELIVERABLE VALIDATION ===")
    errors = []
    
    for filename, file_type in files_to_check:
        full_path = os.path.join(base_dir, filename.replace('/', os.sep))
        print(f"Checking: {filename} ... ", end="")
        
        # 1. Existence Check
        if not os.path.exists(full_path):
            print("[MISSING]")
            errors.append(f"File {filename} does not exist at {full_path}")
            continue
            
        # 2. Size Check
        size = os.path.getsize(full_path)
        if size == 0:
            print("[EMPTY]")
            errors.append(f"File {filename} is empty (0 bytes)")
            continue
            
        # 3. Format Specific Verification
        if file_type == "json":
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Verify key fields
                if "nodes" not in data or "connections" not in data:
                    print("[INVALID WORKFLOW STRUCTURE]")
                    errors.append(f"JSON file {filename} is missing 'nodes' or 'connections' arrays.")
                else:
                    print(f"[OK] ({size} bytes, {len(data['nodes'])} nodes detected)")
            except Exception as e:
                print("[INVALID JSON]")
                errors.append(f"JSON parsing error in {filename}: {str(e)}")
        elif file_type == "binary":
            print(f"[OK] ({size} bytes)")
        else:
            print(f"[OK] ({size} bytes)")
            
    print("==========================================")
    if errors:
        print("[FAIL] VALIDATION FAILED! The following issues were found:")
        for err in errors:
            print(f" - {err}")
        return False
    else:
        print("[SUCCESS] ALL DELIVERABLES VALIDATED SUCCESSFULLY! Project is in clean, submission-ready state.")
        return True

if __name__ == "__main__":
    run_validation()
