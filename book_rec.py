import pandas as pd
import numpy as np

books_df = pd.read_csv('Books.csv',usecols=['ISBN','Book-Title'],dtype={'ISBN': 'str', 'Book-Title': 'str'})
rating_df=pd.read_csv('Ratings.csv',usecols=['User-ID', 'ISBN', 'Book-Rating'],dtype={'User-ID': 'int32', 'ISBN': 'str', 'Book-Rating': 'float32'})


#print(books_df.head())
#print(rating_df.head())

df = pd.merge(rating_df,books_df,on='ISBN')
#print(df.head())

#to drop all null value titles
combine_book_rating = df.dropna(axis = 0, subset = ['Book-Title'])
book_ratingCount = (combine_book_rating.
     groupby(by = ['Book-Title'])['Book-Rating'].
     count().
     reset_index().
     rename(columns = {'Book-Rating': 'totalRatingCount'})
     [['Book-Title', 'totalRatingCount']]
                    
    )
#print(book_ratingCount.head())

rating_with_totalRatingCount = combine_book_rating.merge(book_ratingCount, left_on = 'Book-Title', right_on = 'Book-Title', how = 'left')
#print(rating_with_totalRatingCount.head())


popularity_threshold = 50
rating_popular_book= rating_with_totalRatingCount.query('totalRatingCount >= @popularity_threshold')
#print(rating_popular_book.head())

book_features_df=rating_popular_book.pivot_table(index='Book-Title',columns='User-ID',values='Book-Rating').fillna(0)
print(book_features_df.head())

from scipy.sparse import csr_matrix

book_features_df_matrix = csr_matrix(book_features_df.values)

from sklearn.neighbors import NearestNeighbors


model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
model_knn.fit(book_features_df_matrix)


print(book_features_df.columns)
def getIndexFromTitle(name):
    a=0
    for i in range(book_features_df.shape[0]):
        
        str=book_features_df.index[i]
        
        if(str.casefold()==name.casefold()):
            #print("hello")
            return a
            break
        else:
            a=a+1
    else:
        print("book not found")
        return -1



print(book_features_df)



from tkinter import *

    

def display():
    txt.delete(0.0,"end")
    book=ent.get()
    print(book)
    book_user_has_read=book
    query_index=getIndexFromTitle(book_user_has_read)
    print(query_index)
    if(query_index==-1):
        txt.insert(0.0,"Book not found")
        return
    distances, indices = model_knn.kneighbors(book_features_df.iloc[query_index,:].values.reshape(1, -1), n_neighbors = 6)

    for i in reversed(range(0, len(distances.flatten()))):
        if i == 0:
            txt.insert(0.0,'Recommendations for {0}:\n'.format(book_features_df.index[query_index]))
        else:
            txt.insert(0.0,'{0}: {1}\n'.format(i, book_features_df.index[indices.flatten()[i]]))
        
root=Tk()
root.geometry("420x300")
root.title("Book Recommendation System")

l1=Label(root, text="Enter Book Name:")
l2=Label(root, text="Top Suggetions for You")

ent =Entry(root) 

l1.grid(row=0)
l2.grid(row=2)

ent.grid(row=0,column=1)

txt=Text(root,width=50,height=13,wrap=WORD)
txt.grid(row=3,columnspan=2,sticky=W)

btn=Button(root,text="search",bg="purple",fg="white",command=display)
btn.grid(row=1,columnspan=2)
root.mainloop()
