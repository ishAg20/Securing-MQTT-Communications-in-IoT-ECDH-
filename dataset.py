import pandas as pd
import yaml

conf = yaml.safe_load(open('config.yaml'))
df = pd.read_csv(conf['dataset']['file'])
print(f"Loaded dataset with {len(df)} records.\nLabel distribution:")
print(df[conf['dataset']['label_col']].value_counts())
print("\nSample features:")
print(df[conf['dataset']['features']].head())

