#!/bin/python3
import pandas as pd
import numpy as np
import json

df = pd.read_csv('clases.csv', index_col=[0])
print(df)

df.to_json('s.json') 

