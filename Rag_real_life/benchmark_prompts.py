import pandas as pd
import os
import sys

# Ensure we can find the backend files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
from engine import generate_response
from config import TEMP_MAP

# 1. Hardcoded Test Prompts (targeting specific Nike Policies)
TEST_CASES = [
    {
        "category": "Chemistry",
        "prompt": "New sneakers using a finishing agent with 500ppm Alkylphenol Ethoxylates (APEOs) for moisture-wicking."
    },
    {
        "category": "Conflict Minerals",
        "prompt": "Sourcing Tantalum from a mine in the DRC that is not yet RMAP compliant."
    },
    {
        "category": "Labor Standards",
        "prompt": "A factory requesting a 72-hour work week for the holiday rush with 1.5x overtime pay."
    },
    {
        "category": "Sustainability",
        "prompt": "A new apparel line using 100% recycled polyester from GRS-certified suppliers."
    }
]

def run_benchmark():
    results = []
    
    # We test each prompt with 'Strict' (Temp 0.0) and 'Creative' (Temp 0.8) 
    # to show how hallucinations change with temperature for the PPT.
    for mode in ["Strict Auditor (Fact-Based)", "Creative Strategist"]:
        temp = TEMP_MAP[mode]
        print(f"\n--- Running Benchmark Mode: {mode} (Temp: {temp}) ---")
        
        for case in TEST_CASES:
            print(f"Testing {case['category']}...")
            
            output = generate_response(case['prompt'], temperature=temp)
            
            results.append({
                "Mode": mode,
                "Temperature": temp,
                "Category": case['category'],
                "Prompt": case['prompt'],
                "Latency": output["latency"],
                "Faithfulness": output["faithfulness"],
                "Classification": "Found in Response" if "CLASSIFICATION" in output["answer"] else "N/A",
                "Full_Response": output["answer"]
            })

    # 2. Save to CSV
    df = pd.DataFrame(results)
    output_file = "evaluation_results.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✅ Benchmarking complete! Results saved to {output_file}")

if __name__ == "__main__":
    run_benchmark()