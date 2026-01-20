# prepare_dataset.py
import json, random, argparse, re

def build_output(answers):
    out = []
    for a in answers:
        term = (a.get("term") or "").strip()
        defi = (a.get("definition") or "").strip()
        if term and defi:
            out.append({"term": term, "definition": defi})
    return json.dumps(out, ensure_ascii=False)

def clean(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "")).strip()
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", required=True, help="원본 JSONL (question, answers)")
    ap.add_argument("--train_out", default="train.jsonl")
    ap.add_argument("--eval_out", default="eval.jsonl")
    ap.add_argument("--eval_ratio", type=float, default=0.05)
    args = ap.parse_args()

    data = []
    with open(args.infile, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            ex = json.loads(line)
            q = clean(ex.get("question", ""))
            ans = ex.get("answers", [])
            if not q or not ans: continue
            # 응답을 JSON만 반환하도록 지시
            prompt = f"{q}\n\n정의는 JSON으로만, 키는 term/definition으로 답하세요."
            out = build_output(ans)
            data.append({"input": prompt, "output": out})

    random.shuffle(data)
    n_eval = max(1, int(len(data) * args.eval_ratio))
    eval_set = data[:n_eval]
    train_set = data[n_eval:]

    with open(args.train_out, "w", encoding="utf-8") as f:
        for r in train_set:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(args.eval_out, "w", encoding="utf-8") as f:
        for r in eval_set:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
