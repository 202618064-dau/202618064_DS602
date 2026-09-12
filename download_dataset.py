from sklearn.datasets import fetch_california_housing

# Load the dataset
housing = fetch_california_housing(as_frame=True)

# Convert to a pandas DataFrame
df = housing.frame

# Save the dataset
df.to_csv("data/california_housing.csv", index=False)

print("Dataset downloaded successfully!")
print(df.head())