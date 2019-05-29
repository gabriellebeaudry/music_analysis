# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from pandas import Series, DataFrame
import pandas as pd
from numpy.random import randn
import numpy as np

artists_df = pd.read_table('artists.dat', encoding="utf-8",
                           sep="\t", index_col='id')
artists_df.rename(columns={'id':'artistID'}, inplace=True)

user_artists_df = pd.read_table('user_artists.dat', encoding="utf-8",
                           sep="\t", index_col='userID')
user_friends_df = pd.read_table('user_friends.dat', encoding="utf-8",
                           sep="\t", index_col='userID')
user_taggedartists_df = pd.read_table('user_taggedartists.dat', encoding="utf-8",
                           sep="\t")
#######  SCRATCH CODE ###############################
# use user_artists_df 
#user_artists_df.head()
#list(user_artists_df) #yield column names 
#s = user_artists_df['columnname'] #returns a Series 
#
#user_artists_df.sort_index() # sorts by index - how to sort by a different column? 
#user_artists_df.sort_values(by=['colname']) #play count

####################
def call_print(q): 
    print("")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("")
    print(q)

################### 1: Top artists in terms of play counts. I used the user_artists_df, grouped by artist ID and summed the weight value. Then I sorted the weight value 
top_a = user_artists_df.groupby(['artistID']).sum()
top_a = top_a.join(artists_df).sort_values(by=['weight'], ascending = False).drop(['url','pictureURL'], axis =1)[:10]
call_print('1. Who are the top artists in terms of play counts?')
for index, row in top_a.iterrows(): 
    print('      ', row['name'], '(', index,')  ', row['weight'])


##################### 2: What artists have the most listeners? 
pop_a = user_artists_df.groupby(['artistID']).count()
pop_a = pop_a.join(artists_df).sort_values(by=['weight'], ascending = False).drop(['url','pictureURL'], axis =1)[:10]
call_print('2. What artists have the most listeners?')
for index, row in pop_a.iterrows(): 
    print('      ', row['name'], '(', index,')  ', row['weight'])

#pop_a = pop_a.rename(columns={'weight':'num_users'}, inplace=True) 

###################### 3: Who are the top users in terms of play counts? 
top_u = user_artists_df.groupby(['userID']).sum()
top_u = top_u.join(artists_df).sort_values(by=['weight'], ascending = False).drop(['url','pictureURL', 'artistID', 'name'], axis =1)[:10]
top_u = top_u.reset_index(level=['userID'])
q3 = '3. Who are the top users in terms of play counts?'
call_print(q3) 
for index, row in top_u.iterrows(): 
    print('      ', row['userID'],'   ', row['weight'])


####################### 4: What artists have the highest average number of plays per listener 
#df with artists and total number of plays 
a_plays = user_artists_df.groupby(['artistID']).sum()
a_plays = a_plays.join(artists_df).sort_values(by=['weight'], ascending = False).drop(['url','pictureURL'], axis =1)
a_plays.columns = ['total_plays', 'name']  

#df with artists and total number of listeners 
a_listeners = user_artists_df.groupby(['artistID']).count()
a_listeners = a_listeners.join(artists_df).sort_values(by=['weight'], ascending = False).drop(['url','pictureURL', 'name'], axis =1)
a_listeners.columns = ['total_unique_listeners']

#join prep: drop redundant name column, change duplicate weight name of columns 
a_avg = a_plays.join(a_listeners)
a_avg = a_avg.assign(avg_pl_list= a_avg['total_plays']/a_avg['total_unique_listeners'])
a_avg = a_avg.sort_values(by=['avg_pl_list'], ascending = False) 
a_avg_10 = a_avg.head(10)

call_print('4. What artists have the highest average number of plays per listener?') 
for index, row in a_avg_10.iterrows(): 
    print('      ', row['name'],' (', index, ')', row['total_plays'], ' ',row['total_unique_listeners'],'...Avg: ', int(round(row['avg_pl_list'])))
#*note that this is a lot of *one* user really liking one artist 
    
    
    
####################### 5: What artists *with at least 50 listeners* have the highest average number of plays per listener 
a_avg50 = a_avg[a_avg['total_unique_listeners'] >= 50]
a_avg50_10 = a_avg50.head(10)  
q5 = '5. What artists *with at least 50 listeners* have the highest average number of plays per listener?' 
call_print(q5)
for index, row in a_avg50_10.iterrows(): 
    print('      ', row['name'],' (', index, ')', row['total_plays'], ' ',row['total_unique_listeners'],'...Avg: ', int(round(row['avg_pl_list'])))
#find a way to floor the number 
    
    
    
####################### 6: Do users with five or more friends listen to more songs? 
u_f = user_friends_df.reset_index().groupby(['userID']).count() 
u_f = u_f.reset_index()
u_f.columns = ['userID', 'friendcount'] 
top_u = user_artists_df.groupby(['userID']).sum().drop(['artistID'], axis=1) #index is userID
top_u.columns = ['playcount']

#greater than 5
u_g5 = pd.merge(top_u, u_f[u_f.friendcount>=5], left_index=True, right_on='userID')
avg_g5 = (u_g5['playcount'].sum())/ (u_g5.count() ) 
answer1 = int(avg_g5[0])

### proof of concept ^  
#test = u_g5[:3]
#avg_g5 = (test['playcount'].sum())/ (test.count()) ### checked this manually, it worked  

#less than 5 
u_l5 = pd.merge(top_u, u_f[u_f.friendcount<=5], left_index=True, right_on='userID')
avg_l5 = (u_l5['playcount'].sum())/ (u_l5.count() ) 
answer2 = int(avg_l5[0])
call_print('6. Do users with five or more friends listen to more songs?')
print('            Yes. People with 5 or more friends listen to ', answer1, 'songs on average, compared to people with less than 5 friends, who listen to ', answer2, 'songs on average')  

    
####################### 7: How similar are two artists? 
call_print('7. How similar are two artists?')
user_artists_df.reset_index(level=0, inplace=True)
artists_df.reset_index(level=0, inplace=True)

def artist_sim(aid1, aid2): 
    aid1_u = user_artists_df.loc[user_artists_df['artistID']==aid1]
    set1 = set(pd.Series(aid1_u['userID'].unique()))
    aid2_u = user_artists_df.loc[user_artists_df['artistID']==aid2]
    set2 = set(pd.Series(aid2_u['userID'].unique()))
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    j_index = round((intersection/union), 3)
    
    name1 = artists_df[artists_df['id']==aid1].reset_index().loc[0,'name']
    name2 = artists_df[artists_df['id']==aid2].reset_index().loc[0,'name']
    print('            Artists:',name1, 'and' ,name2, '...Jaccard Index:',j_index)
    

artist_sim(735,562)
artist_sim(735,89)
artist_sim(735,289)
artist_sim(89,289)
artist_sim(89,67)
artist_sim(67,735)

####################### 8: Analysis of top tagged artists 
call_print("8. Analysis of top tagged artists")
tag_df = user_taggedartists_df.reset_index(level=0, inplace=True)
#maybe use 

#




#z = df.groupby('columnname')['enroll'].sum().sort_values(Ascending=False)[:2]








    
    
    
    
    
    
    