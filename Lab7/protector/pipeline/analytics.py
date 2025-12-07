import csv
import os

CSV_HEADERS = [
    'timestamp','file_id','size_original','size_cipher','size_container',
    'time_sign_ms','time_encrypt_ms','time_stego_ms','success_restore','signature_valid'
]

def append_csv_row(output_path, row: dict):
    exists = os.path.exists(output_path)
    with open(output_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not exists:
            writer.writeheader()
        writer.writerow(row)
