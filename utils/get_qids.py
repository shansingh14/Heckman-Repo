#!/usr/bin/env python3
import argparse
import random

def sample_by_qid_txt(input_file, output_file, num_qids, seed=None):
    # 1) Read all lines
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # 2) Parse out (orig_index, qid, raw_line)
    records = []
    for idx, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) < 2:
            continue  # skip blank or malformed
        # second token is "qid:<num>"
        _, qid_token = parts[0], parts[1]
        try:
            qid = qid_token.split(':',1)[1]
        except IndexError:
            continue
        records.append((idx, qid, line))

    # 3) Unique qids
    unique_qids = sorted({qid for _, qid, _ in records})
    rng = random.Random(seed)
    sampled_qids = rng.sample(unique_qids, k=num_qids)

    # 4) Filter records and sort by (qid asc, original index)
    filtered = [rec for rec in records if rec[1] in sampled_qids]
    filtered.sort(key=lambda x: (int(x[1]), x[0]))

    # 5) Write out raw lines exactly
    with open(output_file, 'w') as out:
        for _, _, raw_line in filtered:
            out.write(raw_line)

    print(f"Sampled {len(sampled_qids)} qids ⇒ {len(filtered)} lines → {output_file}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Sample N query‐groups (all docs for each qid) from a space‑delimited LTR .txt"
    )
    p.add_argument("-i", "--input",  required=True, help="full LTR .txt file")
    p.add_argument("-o", "--output", required=True, help="output sampled .txt")
    p.add_argument("-n", "--nqid",   type=int, required=True, help="number of qids to sample")
    p.add_argument("-s", "--seed",   type=int, default=None, help="random seed")
    args = p.parse_args()

    sample_by_qid_txt(args.input, args.output, args.nqid, args.seed)
