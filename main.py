import pandas as pd

# Load all the datasets, not correct filenames rn
# books = pd.read_csv('books.csv')
# users = pd.read_csv('users.csv')
ratings = pd.read_csv('Ratings.csv')

# Filter out rows with 0 ratings
ratings = ratings[ratings['Book-Rating'] != 0]

# Create the utility matrix with a 1% sample size
ratings_sample = ratings.sample(frac=0.0001, random_state=42)
print("Before pivot_table")
utility_matrix = ratings_sample.pivot_table(index='User-ID', columns='ISBN', values='Book-Rating')
print("After pivot_table")


# Print the user IDs in the sample
print("User IDs in the sample:")
print(utility_matrix.index)

# User enters a user id to calculate similar movies for
user = int(input("Enter a user ID (ID number from 1 to 278858 in sample above)"))


# define function to get jaccard similarities, item = book isbn number
def jaccard_similarity(item1, item2, utility_matrixJS, threshold=0):
    users_rated_item1 = set(utility_matrixJS.index[utility_matrixJS[item1] > threshold])
    users_rated_item2 = set(utility_matrixJS.index[utility_matrixJS[item2] > threshold])

    intersection_size = len(users_rated_item1.intersection(users_rated_item2))
    union_size = len(users_rated_item1.union(users_rated_item2))

    similarity = intersection_size / union_size if union_size > 0 else 0
    return similarity


# Extract the values from the utility matrix as a NumPy array
utility_matrix_values = utility_matrix.values

# Calculate item-item Jaccard similarity matrix
print("Before item_similarity_matrix")
item_similarity_matrix = pd.DataFrame(index=utility_matrix.columns, columns=utility_matrix.columns)
for i, item1 in enumerate(utility_matrix.columns):
    for j, item2 in enumerate(utility_matrix.columns):
        item_similarity_matrix.iloc[i, j] = jaccard_similarity(item1, item2, utility_matrix)
print("After item_similarity_matrix")

# Fill NaN values with 0 (assuming missing values mean no similarity)
item_similarity_matrix = item_similarity_matrix.fillna(0)
print(utility_matrix)

# FIX FIX FIX FIX FIX
# User-Based Collaborative Filtering Recommendation
# Function to get top N similar books for a given user based on their preferences
def get_top_similar_books_for_user(user_id, utility_matrix, item_similarity_matrix, num_recommendations=5):
    user_preferences = utility_matrix.loc[user_id]

    # Find books the user has already interacted with
    rated_books = user_preferences[user_preferences > 0].index

    if rated_books.empty:
        return "User has not interacted with any books yet."

    # Calculate a weighted sum of item similarities for each book the user has interacted with
    weighted_sums = item_similarity_matrix[rated_books].sum(axis=1)

    # Exclude books the user has already interacted with
    weighted_sums = weighted_sums[~weighted_sums.index.isin(rated_books)]

    # Get top N recommended books
    top_similar_books = weighted_sums.nlargest(num_recommendations)

    # Get the corresponding similarity scores for the top books
    similarity_scores = item_similarity_matrix.loc[top_similar_books.index, rated_books].sum(axis=1)

    return top_similar_books, similarity_scores


# Get recommendations for the specified user
top_similar_books_for_user, similarity_scores = get_top_similar_books_for_user(user, utility_matrix, item_similarity_matrix)

print(f"\nRecommendations for User {user}:")

# Print ISBNs with their corresponding similarity scores
for isbn, score in zip(top_similar_books_for_user.index, similarity_scores):
    print(f"ISBN: {isbn}, Similarity Score: {score}")
