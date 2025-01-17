import re
from collections import Counter

def count_error_types(file_path):
    """
    Liest Zeile für Zeile 'Gold Result' und 'Predicted Result' aus file_path.
    Kategorisiert jede Vorhersage in genau eine Kategorie:
      1) Bekannte Fehler (error_patterns),
      2) leere Werte ([]),
      3) keine Übereinstimmung (wenn pred: [irgendwas]),
      4) sonstiges (alles andere, was nicht leer und kein bekannter Fehler ist).
    Gibt Counter (error_counts), Liste der keine Übereinstimmungen und Liste der sonstigen Ergebnisse zurück.
    """

    # Bekannte Fehler 
    error_patterns = {
        "no such column": r"no such column",
        "no such table": r"no such table",
        "no such function": r"no such function",
        "syntax error": r"syntax error",
        "leere Werte": r"Predicted Result: \[\]",  # nur für das reine Durchsuchen der Datei
        "ambiguous column name": r"ambiguous column name",
        "misuse of aggregate": r"misuse of aggregate",
    }

    error_counts = Counter()

    nicht_uebereinstimmung_results = []
    sonstiges_results = []

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    mismatch_pattern = r"Gold Result:\s*(.*?)\s*\nPredicted Result:\s*(.*?)\s*\n"
    matches = re.findall(mismatch_pattern, content, flags=re.DOTALL)

    handled_predictions = []

    for gold_result, predicted_result in matches:
        gold_clean = gold_result.strip()
        pred_clean = predicted_result.strip()

        # Prüfschritt 1: Leere Werte ([])
        if pred_clean == "[]":
            error_counts["leere Werte"] += 1
            handled_predictions.append(pred_clean)
            continue

        # Prüfschritt 2: Bekannte Fehler?
        matched_known_pattern = False
        for error_type, pattern in error_patterns.items():
            if re.search(pattern, pred_clean, flags=re.IGNORECASE):
                error_counts[error_type] += 1
                matched_known_pattern = True
                handled_predictions.append(pred_clean)
                break

        if matched_known_pattern:
            continue

        # Prüfschritt 3: Nicht-Übereinstimmung bei [Inhalt]
        if re.match(r"\[\s*\S+.*\]", pred_clean):
            error_counts["keine Übereinstimmung"] += 1
            nicht_uebereinstimmung_results.append((gold_clean, pred_clean))
            handled_predictions.append(pred_clean)
            continue

        # Prüfschritt 4: Alles andere => "sonstiges"
        error_counts["Sonstiges"] += 1
        sonstiges_results.append((gold_clean, pred_clean))
        handled_predictions.append(pred_clean)

    #print in Konsole
    print("Fehleranalyse der unequal.txt:")
    total_errors = sum(error_counts.values())

    for error_type, count in error_counts.items():
        percentage = (count / total_errors * 100) if total_errors else 0
        print(f"{error_type}: {count} ({percentage:.2f} %)")

    if total_errors > 0:
        print(f"\nGesamtanzahl der Fehler: {total_errors} ({(total_errors / total_errors) * 100:.2f} %)")
    else:
        print("\nGesamtanzahl der Fehler: 0 (0.00 %)")

    print("\nNicht-Übereinstimmende Ergebnisse:")
    if nicht_uebereinstimmung_results:
        for gold_res, pred_res in nicht_uebereinstimmung_results:
            print(f"  Gold: {gold_res}")
            print(f"  Pred: {pred_res}\n")
    else:
        print("  Keine Nicht-Übereinstimmungen gefunden.\n")

    print("Sonstige Ergebnisse:")
    if sonstiges_results:
        for gold_res, pred_res in sonstiges_results:
            print(f"  Gold: {gold_res}")
            print(f"  Pred: {pred_res}\n")
    else:
        print("  Keine sonstigen Ergebnisse gefunden.\n")

    return error_counts, nicht_uebereinstimmung_results, sonstiges_results


if __name__ == "__main__":
    file_path = "unequal.txt"
    error_counts, mismatches, sonstiges = count_error_types(file_path)

    #erstelle error_analysis.txt
    with open("error_analysis.txt", "w", encoding="utf-8") as out_file:
        
        # Überschrift
        out_file.write("Fehleranalyse der unequal.txt\n")
        out_file.write("=".center(50, "=") + "\n\n")

        total_errors = sum(error_counts.values())

        # Bereich: Fehler-Typen
        out_file.write("Fehler-Typen und Häufigkeiten:\n")
        out_file.write("-".center(50, "-") + "\n")
        for error_type, count in error_counts.items():
            percentage = (count / total_errors * 100) if total_errors else 0
            out_file.write(f"  • {error_type}: {count} ({percentage:.2f} %)\n")

        # Bereich: Gesamtanzahl
        out_file.write("\n")
        if total_errors > 0:
            out_file.write(f"Gesamtanzahl der Fehler: {total_errors} ({(total_errors / total_errors)*100:.2f} %)\n")
        else:
            out_file.write("Gesamtanzahl der Fehler: 0 (0.00 %)\n")

        # Bereich: Nicht-Übereinstimmungen
        out_file.write("\nNicht-Übereinstimmende Ergebnisse:\n")
        out_file.write("-".center(50, "-") + "\n")
        if mismatches:
            for i, (gold_res, pred_res) in enumerate(mismatches, start=1):
                out_file.write(f"  {i}) Gold: {gold_res}\n")
                out_file.write(f"     Pred: {pred_res}\n\n")
        else:
            out_file.write("  Keine Nicht-Übereinstimmungen gefunden.\n\n")

        # Bereich: Sonstiges
        out_file.write("Sonstige Ergebnisse:\n")
        out_file.write("-".center(50, "-") + "\n")
        if sonstiges:
            for i, (gold_res, pred_res) in enumerate(sonstiges, start=1):
                out_file.write(f"  {i}) Gold: {gold_res}\n")
                out_file.write(f"     Pred: {pred_res}\n\n")
        else:
            out_file.write("  Keine sonstigen Ergebnisse gefunden.\n\n")
