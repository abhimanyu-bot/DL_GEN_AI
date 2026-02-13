import time
from groq import Groq
from config import *
from prompts import AUDITOR_PROMPT, JUDGE_PROMPT
from hybrid_retriever import hybrid_search

client = Groq(api_key=GROQ_API_KEY)

def get_judge_score(context, answer):
    """Benchmarks the faithfulness of the generated answer."""
    try:
        response = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": JUDGE_PROMPT.format(context=context, answer=answer)}],
            temperature=0.0
        )
        return float(response.choices[0].message.content.strip())
    except:
        return 0.5

def generate_response(question, temperature=0.0):
    start_time = time.time()
    
    # 1. Retrieval
    semantic_docs, keyword_docs = hybrid_search(question)
    all_retrieved = semantic_docs + keyword_docs
    context = "\n\n".join([f"[{d.metadata.get('source_file')}] {d.page_content}" for d in all_retrieved])

    # 2. Generation
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": AUDITOR_PROMPT.format(context=context, question=question)}],
        temperature=temperature
    )
    answer = response.choices[0].message.content
    
    # 3. Benchmarking
    latency = time.time() - start_time
    faithfulness = get_judge_score(context, answer)

    return {
        "answer": answer,
        "latency": f"{latency:.2f}s",
        "faithfulness": faithfulness,
        "semantic_chunks": semantic_docs,
        "keyword_chunks": keyword_docs
    }