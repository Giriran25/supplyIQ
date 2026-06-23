import os
files=['DataCoSupplyChainDataset.csv','DescriptionDataCoSupplyChain.csv','tokenized_access_logs.csv']
base=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data','raw')
for f in files:
    p=os.path.join(base,f)
    if os.path.exists(p):
        size=os.path.getsize(p)
        lines=0
        with open(p,'rb') as fh:
            for chunk in iter(lambda: fh.read(1<<20), b''):
                lines += chunk.count(b'\n')
        print(f"{f}\tSizeBytes={size}\tLines={lines}")
    else:
        print(f"{f}\tMISSING")
