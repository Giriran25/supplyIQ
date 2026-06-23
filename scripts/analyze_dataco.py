import csv, sys, os
from collections import defaultdict

p = r'C:\Users\Ranjith Kumar G\Documents\SupplyIQ\data\raw\DataCoSupplyChainDataset.csv'
if not os.path.exists(p):
    print('MISSING', p)
    sys.exit(1)

with open(p, 'r', encoding='utf-8', errors='replace') as f:
    reader = csv.reader(f)
    header = next(reader)
    cols = [h.strip() for h in header]
    ncols = len(cols)
    total = 0
    null_counts = [0]*ncols
    uniqs = [set() for _ in range(ncols)]
    examples = ['']*ncols
    sample_limit = 10
    for row in reader:
        total += 1
        for i in range(ncols):
            v = row[i].strip() if i < len(row) else ''
            if v == '':
                null_counts[i] += 1
            else:
                if len(examples[i])==0:
                    examples[i]=v
                uniqs[i].add(v)
    # prepare output
    print('TOTAL_ROWS=', total)
    print('COLUMN_COUNT=', ncols)
    print('FIELDS:')
    for i, c in enumerate(cols):
        uc = len(uniqs[i])
        null_pct = (null_counts[i]/total*100) if total else 0
        ex = examples[i]
        print(f"{i+1}\t{c}\tNULL%={null_pct:.2f}\tUNIQ={uc}\tEX='{ex}'")
