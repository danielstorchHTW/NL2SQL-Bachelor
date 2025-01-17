import os
import json
import requests
from requests.auth import HTTPBasicAuth
import urllib3
from dotenv import load_dotenv
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables (API Username + Password)
load_dotenv()
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")

# Input & Output Files
questions_input_path = 'spider/dev.json'  
output_file = 'prediction.txt'
tables_json_path = 'spider/tables.json'

# Possible Models for this Evaluation: llama3.2:1b, llama3.2:3b , gemma:7b
model_name = "llama3.2:1b" 

def generate_questions_file():
    """
    Generate the questions.txt file from test.json if it does not exist.
    """
    questions_output_path = 'questions.txt'  

    if os.path.exists(questions_output_path):
        print(f"{questions_output_path} already exists! Skipping questions.txt generation.")
        return

    questions = []

    with open(questions_input_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data:
            question_text = item.get("question", "")
            db_id = item.get("db_id", "unknown_schema")
            if question_text:
                questions.append((question_text, db_id))

    with open(questions_output_path, 'w', encoding='utf-8') as q_file:
        for i, (question, schema) in enumerate(questions, start=1):
            q_file.write(f"Question {i}: {question} ||| {schema}\n")

    print("questions.txt file generated successfully.")

def generate_sql(question, schema_metadata, model):
    """
    Generates SQL query for a given question and schema using the Ollama REST API.
    """
    url = "https://wigpu01l.f4.htw-berlin.de:4000/api/generate"
    auth = HTTPBasicAuth(API_USERNAME, API_PASSWORD)
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": f"""
                    You are a SQL expert. Using the following database schema:

                    {schema_metadata}

                    Write a precise and correct SQL query to answer the following question:

                    {question}

                    The SQL query must adhere to standard SQL conventions and should avoid unnecessary complexity. 
                    Do not include explanations or additional comments, just return the SQL query itself.
                    """,
        "stream": False
    }
    print("\nFrage:\n" + question)
    print("\nSchema:\n" + schema_metadata)
    try:
        response = requests.post(url, auth=auth, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        result = response.json()
        print("\nAntwort:\n" + clean_output(result.get("response", "")))
        print(f"\n{'-'*100}\n")

        return clean_output(result.get("response", ""))
    except requests.exceptions.RequestException as e:
        print(f"Error calling the API: {e}")
        return "ERROR: API call failed."

def load_schema(database_name):
    """
    Loads the Schema for the specified database from tables.json.
    """
    if not os.path.exists(tables_json_path):
        print("Error: file not found!")
        return None

    # Load the JSON data
    with open(tables_json_path, 'r', encoding='utf-8') as f:
        tables_data = json.load(f)

    # Find the schema for the given database
    for db in tables_data:
        if db['db_id'] == database_name:
            # Format schema metadata as a string for the API
            tables = db["table_names_original"]
            columns = db["column_names_original"]
            foreign_keys = db["foreign_keys"]
            primary_keys = db["primary_keys"]

            schema_metadata = []
            for table_idx, table_name in enumerate(tables):
                schema_metadata.append(f"Table: {table_name}")
                schema_columns = [
                    col[1] for col in columns if col[0] == table_idx
                ]
                schema_metadata.append(f"  Columns: {', '.join(schema_columns)}")

                # Adding Primarykey 
                pk_columns = [
                    columns[pk][1] for pk in primary_keys if columns[pk][0] == table_idx
                ]
                if pk_columns:
                    schema_metadata.append(f"  Primary Key: {', '.join(pk_columns)}")
            
            if foreign_keys:
                schema_metadata.append("\nForeign Keys:")
                for fk in foreign_keys:
                    table_a = tables[columns[fk[0]][0]]  # Table of foreign key
                    table_b = tables[columns[fk[1]][0]]  # Table of referenced key
                    column_a = columns[fk[0]][1]  # Column of foreign key
                    column_b = columns[fk[1]][1]  # Column of referenced key
                    schema_metadata.append(f"  {table_a}.{column_a} -> {table_b}.{column_b}")

            return "\n".join(schema_metadata)

    print(f"Schema not found in DB: {database_name}")
    return None

def clean_output(raw_sql):
    """
    Cleans the raw SQL output to remove Markdown markers.
    """
    # Remove unnecessary text or explanations
    if "```sql" in raw_sql:
        raw_sql = raw_sql.split("```sql")[-1]  # Get content after "```sql"
    if "```" in raw_sql:
        raw_sql = raw_sql.split("```")[0]  # Remove everything after closing "```"

    # Remove leading and trailing whitespace
    return raw_sql.strip()

def main():
    # Check if the questions_input_path file exists
    if not os.path.exists(questions_input_path):
        print(f"{questions_input_path} not found.")
        return

    print(f"{questions_input_path} found.")
    generate_questions_file()

    # Read questions from the generated questions.txt file
    with open('questions.txt', 'r', encoding='utf-8') as f:
        questions = f.readlines()

    # Open the output file to write the generated SQL queries
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, question in enumerate(questions, start=1):
            question = question.strip()
            if question:  
                # Extract database name from the question (assumes `|||` separates it)
                parts = question.split("|||")
                if len(parts) < 2:
                    print(f"Invalid format for question {idx}: {question}")
                    continue
                database_name = parts[1].strip()
                schema_metadata = load_schema(database_name)

                if not schema_metadata:
                    f.write(f"Question {idx}: {question}\n")
                    f.write("SQL: ERROR: Schema not found.\n\n")
                    continue

                print(f"Generating SQL for {question}")
                sql_query = generate_sql(parts[0].strip(), schema_metadata, model_name)
                # Remove all semicolons and \n from the SQL query
                sql_query = sql_query.replace(";", "").replace("\n", " ")
                f.write(f"{sql_query}\t{database_name}\n")
    print(f"SQL queries saved to {output_file}")

if __name__ == "__main__":
    main()