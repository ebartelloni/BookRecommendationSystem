import pandas as pd

# Load all the datasets
books = pd.read_csv('Book2.csv')
ratings = pd.read_csv('Rating2.csv')

# Filter out rows with 0 ratings
ratings = ratings[ratings['Book-Rating'] != 0]

# Create the utility matrix with a 1% sample size
# ratings_sample = ratings.sample(frac=0.0001, random_state=42)
print("Before pivot_table")
# utility_matrix = ratings_sample.pivot_table(index='User-ID', columns='ISBN', values='Book-Rating')
utility_matrix = ratings.pivot_table(index='User-ID', columns='ISBN', values='Book-Rating')
print("After pivot_table")


# Print the user IDs in the sample
print("User IDs in the sample:")
print(utility_matrix.index)

# User enters a user id to calculate similar movies for
user = int(input("Enter a user ID (ID number from 1 to 100 in sample above)"))


# define function to get jaccard similarities, item = book isbn number
def jaccard_similarity(item1, item2, utility_matrixJS, threshold=0):
    users_rated_item1 = set(utility_matrixJS.index[utility_matrixJS[item1] > threshold])
    users_rated_item2 = set(utility_matrixJS.index[utility_matrixJS[item2] > threshold])

    intersection_size = len(users_rated_item1.intersection(users_rated_item2))
    union_size = len(users_rated_item1.union(users_rated_item2))

    similarity = intersection_size / union_size if union_size > 0 else 0
    return similarity


# Calculate item-item Jaccard similarity matrix - costly?
print("Before item_similarity_matrix")
item_similarity_matrix = pd.DataFrame(index=utility_matrix.columns, columns=utility_matrix.columns)
for i, item1 in enumerate(utility_matrix.columns):
    for j, item2 in enumerate(utility_matrix.columns):
        item_similarity_matrix.iloc[i, j] = jaccard_similarity(item1, item2, utility_matrix)
print("After item_similarity_matrix")

# Fill NaN values w 0
item_similarity_matrix = item_similarity_matrix.fillna(0)

# funtion that gets similar books for user
def get_top_similar_books_for_user(user_id, utility_matrix, item_similarity_matrix, books, num_recommendations=5):
    user_preferences = utility_matrix.loc[user_id]

    # find books the user has/hasn't read and calculate sum of item similarities
    rated_books = user_preferences[user_preferences > 0].index
    if rated_books.empty:
        return "User has not interacted with any books yet."

    weighted_sums = item_similarity_matrix[rated_books].sum(axis=1)

    # exclude books the user has already read and get recomended
    weighted_sums = weighted_sums[~weighted_sums.index.isin(rated_books)]
    top_similar_books = weighted_sums.nlargest(num_recommendations)

    # Get data about books and store it to print
    top_books_info = pd.DataFrame({
        'ISBN': top_similar_books.index,
        'Book-Title': books.set_index('ISBN').loc[top_similar_books.index, 'Book-Title'],
        'Book-Author': books.set_index('ISBN').loc[top_similar_books.index, 'Book-Author'],
        'Similarity Score': item_similarity_matrix.loc[top_similar_books.index, rated_books].sum(axis=1)
    })
    # reset index so we don't print ISBN's twice
    top_books_info.reset_index(drop=True, inplace=True)

    return top_books_info


# Get recommendations for the specified user
top_similar_books = get_top_similar_books_for_user(user, utility_matrix, item_similarity_matrix, books)

# display all rows and columns and print result
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(f"\nRecommendations for User {user}:")
print(top_similar_books)
