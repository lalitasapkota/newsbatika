# import re

# import nltk
# from django.http import HttpResponse
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# from .models import Headline
# # from .models import Headline

# # Download NLTK data packages if not already downloaded
# nltk.download("punkt")
# nltk.download("stopwords")


# # Tokenize and preprocess function
# def tokenize_and_preprocess(text):
#     stop_words = set(stopwords.words("english"))
#     text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
#     word_tokens = word_tokenize(text.lower())  # Tokenize and convert to lowercase
#     filtered_text = [
#         word for word in word_tokens if word not in stop_words
#     ]  # Remove stopwords
#     return " ".join(filtered_text)


# # Function to calculate cosine similarity
# def calculate_cosine_similarity(query_vector, document_vectors):
#     similarities = cosine_similarity(query_vector.reshape(1, -1), document_vectors)
#     return similarities.flatten()


# # Function to calculate similarity with models
# def calculate_similarity_with_models(query):
#     # Word to compare
#     query_word = query

#     # Retrieve text data from Django models
#     documents = Headline.objects.values_list("title", flat=True)

#     # Tokenize and preprocess the query word
#     query_text = tokenize_and_preprocess(query_word)

#     # Tokenize and preprocess the documents
#     preprocessed_documents = [
#         tokenize_and_preprocess(document) for document in documents
#     ]

#     # Vectorize using TF-IDF
#     vectorizer = TfidfVectorizer()
#     document_vectors = vectorizer.fit_transform(preprocessed_documents)

#     # Vectorize the query word
#     query_vector = vectorizer.transform([query_text])

#     # Calculate cosine similarity
#     similarities = calculate_cosine_similarity(query_vector, document_vectors)

#     similar = []
#     for i, value in enumerate(similarities):
#         if value > 0:
#             # Append the element from list2 corresponding to the index where list1 has a value of 1
#             similar.append(documents[i])
#     similar_obj = Headline.objects.filter(title__in=similar)
#     print(similarities, " cosine similarities::\n\n", similar_obj)
#     return similar_obj
#     print(similar_obj)
#     print(similarities, " cosine similarities")
#     return HttpResponse(similarities)
