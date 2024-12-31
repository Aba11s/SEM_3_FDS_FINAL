import pandas as pd
from scipy.stats import pointbiserialr

# importing data
data = pd.read_csv("data/final_pmr.csv")

# selecting target label
target = data['winner']

output = pd.DataFrame(
    columns=[
        "feature",
        "correlation",
        "p_value"
    ]
)

# iterating over all columns
for col in data.columns[2:14]:

    variable = data[col]

    # calculates the correlation, as well as the p-value
    correlation, p_value = pointbiserialr(target, variable)

    print("feature: ", col)
    print("Point-Biserial Correlation: ", correlation)
    print("P-value: ", p_value)

    output.loc[len(output)] = [col, correlation, p_value]

# sort df by correlation/p-value
output.sort_values(by="correlation", ascending=False, inplace=True)

# resets the index so it is sorted
output.reset_index(inplace=True, drop=True)
output.to_csv("output/point-biserial-output.csv")