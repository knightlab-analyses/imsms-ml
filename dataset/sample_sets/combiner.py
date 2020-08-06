import pandas as pd

df = pd.read_csv("0.csv", header=None)
df.columns = [str(0)]

for i in range(1, 100):
    col = pd.read_csv(str(i)+".csv", header=None)
    col.columns = [str(i)]
    df = df.join(col)

df.to_csv("fixed_training_sets.csv")
print(df)