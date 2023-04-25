import numpy as np
import scipy.sparse as sparse
from sklearn.preprocessing import MinMaxScaler
from .spotify_functions import top_recs_to_string

def implicit_recommend(user_id, sparse_user_item, model, song_infos, num_to_id, num_items):
    
    user_vecs = sparse.csr_matrix(model.user_factors)
    item_vecs = sparse.csr_matrix(model.item_factors)
    
    user_interactions = sparse_user_item[user_id,:].toarray()

    user_interactions = user_interactions.reshape(-1) + 1
    user_interactions[user_interactions > 1] = 0

    rec_vector = user_vecs[user_id,:].dot(item_vecs.T).toarray()

    min_max = MinMaxScaler()
    rec_vector_scaled = min_max.fit_transform(rec_vector.reshape(-1,1))[:,0]
    recommend_vector = user_interactions * rec_vector_scaled

    item_idx = np.argsort(recommend_vector)[::-1][:num_items]

    return top_recs_to_string(top_recs=item_idx, song_infos=song_infos, num_to_id=num_to_id), item_idx