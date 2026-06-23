import os
import csv
from collections import Counter
from datetime import datetime

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')

def infer_type(samples):
    # simple inference: int, float, date, string
    types = set()
    for s in samples:
        if s is None or s == '':
            types.add('null')
            continue
        v = s.strip()
        # int
        try:
            int(v)
            types.add('int')
            continue
        except:
            pass
        try:
            float(v)
            types.add('float')
            continue
        except:
            pass
        # date
        for fmt in ('%Y-%m-%d','%Y-%m-%d %H:%M:%S','%m/%d/%Y','%Y/%m/%d'):
            try:
                datetime.strptime(v, fmt)
                types.add('date')
                break
            except:
                pass
        else:
            types.add('string')
    # prioritize
    if 'string' in types:
        return 'string'
    if 'date' in types:
        return 'date'
    if 'float' in types:
        return 'float'
    if 'int' in types:
        return 'int'
    if 'null' in types:
        return 'null'
    return 'string'


def analyze_csv(path, max_samples=1000):
    info = {}
    info['path'] = path
    info['size_bytes'] = os.path.getsize(path)
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            header = []
        info['cols'] = [h.strip() for h in header]
        col_count = len(info['cols'])
        info['col_count'] = col_count
        # collect samples per column
        samples = [[] for _ in range(col_count)]
        row_count = 0
        for row in reader:
            row_count += 1
            if row_count <= max_samples:
                for i in range(col_count):
                    val = row[i] if i < len(row) else ''
                    samples[i].append(val)
        # count nulls across scanned rows
        nulls = []
        examples = []
        dtypes = []
        for col_samples in samples:
            n_null = sum(1 for v in col_samples if v is None or v.strip() == '')
            nulls.append((n_null, len(col_samples)))
            examples.append(next((v for v in col_samples if v is not None and v.strip() != ''), '' ))
            dtypes.append(infer_type(col_samples[:50]))
        info['rows_sampled'] = min(row_count, max_samples)
        # get total rows by fast count
    # total rows
    with open(path, 'rb') as f:
        total_lines = 0
        for _ in f:
            total_lines += 1
    # subtract header
    info['total_rows'] = max(0, total_lines - 1)
    info['nulls'] = nulls
    info['examples'] = examples
    info['dtypes'] = dtypes
    return info


def main():
    if not os.path.isdir(RAW_DIR):
        print('data/raw not found at', RAW_DIR)
        return
    files = sorted([f for f in os.listdir(RAW_DIR) if f.lower().endswith('.csv')])
    if not files:
        print('No CSV files found in data/raw')
        return
    results = []
    for f in files:
        path = os.path.join(RAW_DIR, f)
        print('\n== FILE:', f)
        info = analyze_csv(path)
        print(' Size (bytes):', info['size_bytes'])
        print(' Total rows:', info['total_rows'])
        print(' Column count:', info['col_count'])
        print(' Columns:')
        for i, col in enumerate(info['cols']):
            null_cnt, sampled = info['nulls'][i]
            null_pct = (null_cnt / sampled * 100) if sampled else 0
            print(f"  - {col} | type={info['dtypes'][i]} | null% (sample)={null_pct:.1f}% | example='{info['examples'][i]}'")
        results.append(info)

if __name__ == '__main__':
    main()
