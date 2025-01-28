import re
from collections import Counter

def count_error_types(file_path):
    """
    Reads 'Gold Result' and 'Predicted Result' line by line from file_path.
    Categorizes each prediction into exactly one category:
      1) Known errors (error_patterns),
      2) empty values ([]),
      3) no match (if pred: [something]),
      4) others (anything that is not empty and not a known error).
    Returns a Counter (error_counts), a list of no matches, and a list of other results.
    """

    # Known errors
    error_patterns = {
        "no such column": r"no such column",
        "no such table": r"no such table",
        "no such function": r"no such function",
        "syntax error": r"syntax error",
        # This pattern is kept for searching, even though we directly check for [] below.
        "empty values": r"Predicted Result: \[\]",  
        "ambiguous column name": r"ambiguous column name",
        "misuse of aggregate": r"misuse of aggregate",
    }

    error_counts = Counter()

    no_match_results = []
    others_results = []

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    mismatch_pattern = r"Gold Result:\s*(.*?)\s*\nPredicted Result:\s*(.*?)\s*\n"
    matches = re.findall(mismatch_pattern, content, flags=re.DOTALL)

    for gold_result, predicted_result in matches:
        gold_clean = gold_result.strip()
        pred_clean = predicted_result.strip()

        # Check step 1: Empty values ([])
        if pred_clean == "[]":
            error_counts["empty values"] += 1
            continue

        # Check step 2: Known errors?
        matched_known_pattern = False
        for error_type, pattern in error_patterns.items():
            if re.search(pattern, pred_clean, flags=re.IGNORECASE):
                error_counts[error_type] += 1
                matched_known_pattern = True
                break

        if matched_known_pattern:
            continue

        # Check step 3: No match if [something]
        if re.match(r"\[\s*\S+.*\]", pred_clean):
            error_counts["no match"] += 1
            no_match_results.append((gold_clean, pred_clean))
            continue

        # Check step 4: Everything else => "others"
        error_counts["others"] += 1
        others_results.append((gold_clean, pred_clean))

    # Print to console
    print("Error analysis of unequal.txt:")
    total_errors = sum(error_counts.values())

    for error_type, count in error_counts.items():
        percentage = (count / total_errors * 100) if total_errors else 0
        print(f"{error_type}: {count} ({percentage:.2f} %)")

    if total_errors > 0:
        print(f"\nTotal number of errors: {total_errors} ({(total_errors / total_errors) * 100:.2f} %)")
    else:
        print("\nTotal number of errors: 0 (0.00 %)")

    print("\nNo-match results:")
    if no_match_results:
        for gold_res, pred_res in no_match_results:
            print(f"  Gold: {gold_res}")
            print(f"  Pred: {pred_res}\n")
    else:
        print("  No mismatches found.\n")

    print("Other results:")
    if others_results:
        for gold_res, pred_res in others_results:
            print(f"  Gold: {gold_res}")
            print(f"  Pred: {pred_res}\n")
    else:
        print("  No other results found.\n")

    return error_counts, no_match_results, others_results


if __name__ == "__main__":
    file_path = "unequal.txt"
    error_counts, mismatches, others = count_error_types(file_path)

    # Create error_analysis.txt
    with open("error_analysis.txt", "w", encoding="utf-8") as out_file:
        
        # Heading
        out_file.write("Error analysis of unequal.txt\n")
        out_file.write("=".center(50, "=") + "\n\n")

        total_errors = sum(error_counts.values())

        # Section: Error types
        out_file.write("Error types and frequencies:\n")
        out_file.write("-".center(50, "-") + "\n")
        for error_type, count in error_counts.items():
            percentage = (count / total_errors * 100) if total_errors else 0
            out_file.write(f"  • {error_type}: {count} ({percentage:.2f} %)\n")

        # Section: Total count
        out_file.write("\n")
        if total_errors > 0:
            out_file.write(f"Total number of errors: {total_errors} ({(total_errors / total_errors)*100:.2f} %)\n")
        else:
            out_file.write("Total number of errors: 0 (0.00 %)\n")

        # Section: No-match results
        out_file.write("\nNo-match results:\n")
        out_file.write("-".center(50, "-") + "\n")
        if mismatches:
            for i, (gold_res, pred_res) in enumerate(mismatches, start=1):
                out_file.write(f"  {i}) Gold: {gold_res}\n")
                out_file.write(f"     Pred: {pred_res}\n\n")
        else:
            out_file.write("  No mismatches found.\n\n")

        # Section: Other results
        out_file.write("Other results:\n")
        out_file.write("-".center(50, "-") + "\n")
        if others:
            for i, (gold_res, pred_res) in enumerate(others, start=1):
                out_file.write(f"  {i}) Gold: {gold_res}\n")
                out_file.write(f"     Pred: {pred_res}\n\n")
        else:
            out_file.write("  No other results found.\n\n")
