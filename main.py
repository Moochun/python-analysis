#!/usr/bin/env python
# coding: utf-8

# # Data load and clean 

# In[15]:


import pandas as pd 
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import sweetviz as sv
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
import seaborn as sns
import matplotlib.pyplot as plt
from funcs import feature_engineer as fe


# In[2]:


# 1. Load data 
df_data = pd.read_csv("data/uselog.csv")


# 2. Time clean # Missing eliminate
df_data["timestamp"] = pd.to_datetime(df_data["timestamps of usage"])
df_data = fe.crt_multiple_timestamp_columns(df_data, "timestamp")
df_data =df_data.loc[~df_data["timestamp"].isna(),]

#3. User data create 
ufe = fe.UserFE(df_data)
df_user = ufe.crt_user_features()

# 3. Save result 
df_data.to_csv("data/uselog_fe.csv")
# del df_data["timestamps of usage"]


# # Data description & Basic EDA

# In[3]:


# 1. Data description with sweetviz analysis to know the basic info 
# 1-1. Function usage event : 181,978 functions call
report = sv.analyze(df_data, pairwise_analysis="off")
report.show_html('report/SweetvizBascInfo.html')

# 1-2. User basic info : 237 people
report_user = sv.analyze(df_user, pairwise_analysis="off")
report_user.show_html('report/SweetvizUser.html')
user_multitype_num = (df_user["user type"].str.len()>=2).sum()

print(f"Users with multi user type : {user_multitype_num}")
print(f"Timestamp Start : {df_data['timestamp'].min()}, Timestamp End {df_data['timestamp'].max()}")


# In[24]:


# 2.Histogram 繪製每日的使用量
df_data["date"] = df_data["timestamp"].dt.date
fig = go.Figure()
fig = px.histogram(df_data, x='date', nbins=len(df_data['date'].unique()), title='Histogram of Date', histfunc='count')
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Count',
    bargap=0.1,
    xaxis_range=[df_data["date"].min(), df_data["date"].max()]
)
fig.show()


# # Customer segment 

# ## 黏著度 + 使用特徵數量

# In[22]:


# 0. 抓取對應的Attributes
df_user["CustomerStickness"]=df_user["DayUsageRatio"]
df_user["FunctionUsageBreadth"]=df_user["FunctionUsageBreadth"]
col_b = "FunctionUsageBreadth"
# 1. 繪製散點圖
fig = px.scatter(
    df_user, x='CustomerStickness', y=col_b, 
    title='Customer Stickiness vs Function Usage Breadth',
    labels={'CustomerStickness': 'Customer Stickiness', col_b: 'Function Usage Breadth'},
    color_discrete_sequence=['deepskyblue'],  
    hover_data={'ID': True, 'CustomerStickness': True, col_b: True} # 設置 hover 可以顯示ID名稱
)

fig.update_layout(
    xaxis_title='Customer Stickiness',
    yaxis_title='Function Usage Breadth'
)

# 2. 中位數線
median_customer_stickness = df_user['CustomerStickness'].median()
median_function_usage_breadth = df_user[col_b].median()
fig.add_shape(type='line', x0=median_customer_stickness, y0=df_user[col_b].min(),
              x1=median_customer_stickness, y1=df_user[col_b].max(),
              line=dict(color='gray', width=2))

fig.add_shape(type='line', x0=df_user['CustomerStickness'].min(), y0=median_function_usage_breadth,
              x1=df_user['CustomerStickness'].max(), y1=median_function_usage_breadth,
              line=dict(color='gray', width=2))

fig.show()


# ## 黏著度+使用function

# ### Kmeans

# In[48]:


#2. Kmeans 分群
df_user["CustomerStickness"]=df_user["DayUsageRatio"]
col_a = "CustomerStickness"
col_b = "TotalUsage"
col_b_ratio = col_b+"_ratio"
df_user[col_b_ratio]=df_user[col_b]/max(df_user[col_b])

kmeans = KMeans(n_clusters=5, random_state=0)
df_user['cluster'] = kmeans.fit_predict(df_user[[col_a, col_b_ratio]])

# Plot the result, by coloring the label
sns.scatterplot(data=df_user, x=col_a, y=col_b_ratio, hue='cluster', palette='viridis')
plt.title('K-means Clustering')
plt.xlabel(col_a)
plt.ylabel(col_b_ratio)
plt.show()


# ### 一般的散佈圖

# In[44]:


# 0. 抓取對應的Attributes
df_user["CustomerStickness"]=df_user["DayUsageRatio"]
col_a = "CustomerStickness"
col_b = "TotalUsage"
# 1. 繪製散點圖
fig = px.scatter(
    df_user, x=col_a, y=col_b, 
    title=f'{col_a} vs {col_b}',
    labels={col_a: col_a, col_b: col_b},
    color_discrete_sequence=['deepskyblue'],  
    # color='cluster',
    hover_data={'ID': True, col_a: True, col_b: True} # 設置 hover 可以顯示ID名稱
)

fig.update_layout(
    xaxis_title=col_a,
    yaxis_title=col_b
)

# 2. 中位數線
median_cola= df_user[col_a].median()
median_colb = df_user[col_b].median()
print(f"{col_a}Median : {median_cola}")
print(f"{col_b}Median : {median_colb}")

fig.add_shape(type='line', x0=median_cola, y0=df_user[col_b].min(),
              x1=median_cola, y1=df_user[col_b].max(),
              line=dict(color='gray', width=2))

fig.add_shape(type='line', x0=df_user[col_a].min(), y0=median_colb,
              x1=df_user[col_a].max(), y1=median_colb,
              line=dict(color='gray', width=2))

fig.show()

#3. 標註各群體的標籤
df_user["group"] = np.select(
    [
        (df_user[col_a]<= median_cola) & (df_user[col_b]<= median_colb),
        (df_user[col_a]<= median_cola) & (df_user[col_b]> median_colb),
        (df_user[col_a]> median_cola) & (df_user[col_b]> median_colb),
        (df_user[col_a]> median_cola) & (df_user[col_b]<= median_colb)
    ],
    [
        1,2,3,4
    ]
)
print(df_user["group"].value_counts())


# ### Cluster上色後的散佈圖

# In[49]:


# 0. 抓取對應的Attributes
df_user["CustomerStickness"]=df_user["DayUsageRatio"]
col_a = "CustomerStickness"
col_b = "TotalUsage"
# 1. 繪製散點圖
fig = px.scatter(
    df_user, x=col_a, y=col_b, 
    title=f'{col_a} vs {col_b}',
    labels={col_a: col_a, col_b: col_b},
    # color_discrete_sequence=['deepskyblue'],  
    color='cluster',
    hover_data={'ID': True, col_a: True, col_b: True} # 設置 hover 可以顯示ID名稱
)

fig.update_layout(
    xaxis_title=col_a,
    yaxis_title=col_b
)

# 2. 中位數線
median_cola= df_user[col_a].median()
median_colb = df_user[col_b].median()
print(f"{col_a}Median : {median_cola}")
print(f"{col_b}Median : {median_colb}")

fig.add_shape(type='line', x0=median_cola, y0=df_user[col_b].min(),
              x1=median_cola, y1=df_user[col_b].max(),
              line=dict(color='gray', width=2))

fig.add_shape(type='line', x0=df_user[col_a].min(), y0=median_colb,
              x1=df_user[col_a].max(), y1=median_colb,
              line=dict(color='gray', width=2))

fig.show()

#3. 標註各群體的標籤
df_user["group"] = np.select(
    [
        (df_user[col_a]<= median_cola) & (df_user[col_b]<= median_colb),
        (df_user[col_a]<= median_cola) & (df_user[col_b]> median_colb),
        (df_user[col_a]> median_cola) & (df_user[col_b]> median_colb),
        (df_user[col_a]> median_cola) & (df_user[col_b]<= median_colb)
    ],
    [
        1,2,3,4
    ]
)
print(df_user["cluster"].value_counts())


# ### Infrequent User

# In[51]:


# Function calling compare 
report_infrquent_function= sv.compare(
    [df_data, "All user"], 
    [df_data[df_data.ID.isin(df_user.ID[df_user["cluster"]==0])], "Infrequent user"], 
    pairwise_analysis="off"
)
report_infrquent_function.show_html('report/SweetvizUserInfrequent_functions.html')

# User compare
report_infrquent= sv.compare(
    [df_user, "All user"], 
    [df_user[df_user["cluster"]==0], "Infrequent user"], 
    pairwise_analysis="off"
)
report_infrquent.show_html('report/SweetvizUserInfrequent.html')


# In[52]:


df_data[df_data.ID.isin(df_user.ID[df_user["cluster"]==0])]


# # Function Usage

# ## Function 被呼叫數量直方圖

# In[61]:


# 1. 繪製使用量, 抓出使用量最低的functions
# 排序結果
col_x = "function"
category_counts = df_data[col_x].value_counts().reset_index()
category_counts.columns = [col_x, 'Count']
category_counts = category_counts.sort_values(by='Count', ascending=False)
df_data[col_x] = pd.Categorical(df_data[col_x], categories=category_counts[col_x], ordered=True)

# 創建圖形
fig = go.Figure()
fig = px.histogram(df_data, x=col_x, category_orders={col_x: category_counts[col_x]},
                   title='Histogram Sorted by Count',
                   labels={col_x: col_x, 'count': 'Count'})
fig.update_layout(
    xaxis_title=col_x,
    yaxis_title='Count',
    bargap=0.1
)
fig.show()


# ## Function user數量直方圖

# In[69]:


# 2. 繪製使用量, 抓出使用人最少的functions
# 排序結果
col_x = "function"
category_users = df_data.groupby(col_x).agg(UserCounts=("ID", "nunique")).reset_index()
category_users.columns = [col_x, 'UserCounts']
category_users = category_users.sort_values(by='UserCounts', ascending=False)
df_data[col_x] = pd.Categorical(df_data[col_x], categories=category_users[col_x], ordered=True)

# 創建圖形
fig = go.Figure()
fig = px.bar(category_users, x=col_x,  y='UserCounts', 
             title='Unique ID Count per Function',
             labels={'Function': 'Function', 'UserCounts': 'UserCounts'})
fig.update_layout(
    xaxis_title=col_x,
    yaxis_title='UserCounts',
    bargap=0.1
)
fig.show()


# # 繪圖區

# In[ ]:


# 創建圖形
fig = go.Figure()
fig = px.histogram(df_proportions, x='Afternoon', nbins=10, title='Histogram of Values')
fig.show()


# In[23]:


# 創建圖形
df_data["date"] = df_data["timestamp"].dt.date
fig = go.Figure()
fig = px.histogram(df_data, x='date', nbins=len(df_data['date'].unique()), title='Histogram of Date', histfunc='count')
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Count',
    bargap=0.1,
    xaxis_range=[df_data["date"].min(), df_data["date"].max()]
)
fig.show()


# In[22]:


len(df_data['date'].unique())

