import numpy as np
import pandas as pd
def get_time_of_day(hours):
    hour_tags = np.select(
        [
            (6 <= hours) & (hours < 12),
            (12 <= hours) & (hours < 18),
            (18 <= hours) & (hours < 24)
        ],
        [
            "Morning",
            "Afternoon",
            "Evening"
        ],
        "Midnight"
    )
    return(hour_tags)
    
    
def crt_multiple_timestamp_columns(df, col_datetime) : 
    timestamp = df[col_datetime]
    df["month"] = timestamp.dt.month
    df["day_name"] = timestamp.dt.day_name()
    df["hour_24"] = timestamp.dt.hour
    df["time_of_day"] = get_time_of_day(timestamp.dt.hour)
    df["is_weekend"] = timestamp.dt.weekday >= 5  # 5 means Saturday，6 means Sunday

    return(df)

class UserFE():
    def __init__(self, df_system):
        """
        """
        self.df_system = df_system     

    def crt_user_type(self, df_system):
        """
        """
        df_user_tmp = df_system.groupby('ID').agg({
            'user type': lambda x: ''.join(sorted(set(x)))  # 假設你只想保留第一個使用日期，具體取決於你的需求
        }).reset_index()
        
        return(df_user_tmp)
        
    def crt_total_usage(self, df_system):
        """
        Args : 
            df_system : pd.DataFrame
                with column "ID"
        """
        # 1. 3個月的總使用次數
        df_grouped = df_system.groupby("ID").agg(
             TotalUsage=("ID", "count")  
        ).reset_index()

        # 2. Create Final DataFrame
        df_tmp = pd.DataFrame(
            {
                "ID" : df_grouped["ID"],
                "TotalUsage" : df_grouped["TotalUsage"]
            }
        )
        return(df_tmp)
        
    def crt_time_of_day_propotions(self, df_system):
        """
        Args : 
            df_system : pd.DataFrame 
                with column "ID", "time_of_day"
        Return : 
            pd.DataFrame : 
                with The proprtion in different time slot "Morning", "Afternoon", "Evenning", "Midnight" 
        """
        # 1. 各時段比例
        # 計算每個時間段的使用次數
        # 計算每個 ID 的總使用次數，用於計算比例
        # 計算比例
        df_time_counts = df_system.groupby(['ID', 'time_of_day']).size().unstack(fill_value=0)
        df_total_counts = df_time_counts.sum(axis=1)
        df_proportions = df_time_counts.divide(df_total_counts, axis=0)
        df_proportions = df_proportions.reset_index()

        # 2. Create Final DataFrame
        df_tmp = pd.DataFrame(
            {
                "ID" : df_proportions["ID"],
                "Morning" : df_proportions["Morning"],
                "Afternoon" : df_proportions["Afternoon"],
                "Evening" : df_proportions["Evening"],
                "Midnight" : df_proportions["Midnight"]
            }
        )
        return(df_tmp)

    def crt_day_propotion(self, df_system):
        """" The User's usage proportion in the system logs by day level
        Args : 
            df_system : pd.DataFrame 
                with column "ID", "timestamp"
        Return : 
            pd.DataFrame : 
                with "DayUsage", "DayUsageProportion" 
        """

        # 0. Date initialize settings 
        series_timestamp = df_system["timestamp"]
        day_interval = (series_timestamp.max()-series_timestamp.min()).days
        
        # 1.黏著度(每天使用,還是某幾天在用)
        df_system["date"] = series_timestamp.dt.to_period('D')
        df_grouped = df_system.groupby("ID").agg(
             DayUsage=("date", "nunique")  
        ).reset_index()

        # 2. Create Final DataFrame
        df_tmp = pd.DataFrame(
            {
                "ID" : df_grouped["ID"],
                "DayUsage" : df_grouped["DayUsage"],
                "DayUsageRatio" : df_grouped["DayUsage"]/day_interval # 用整個樣本的區間做計算比較
            }
        )
        return(df_tmp)
    

        
    def crt_user_features(self):
        """
        """
        df_user = self.df_system.loc[:,["ID"]].drop_duplicates()
        df_user = df_user.merge(self.df_system.loc[:,["ID", "place of residence"]].drop_duplicates(), on="ID", how="left")
        df_user = df_user.merge(self.crt_user_type(self.df_system), on="ID", how="left")
        df_user = df_user.merge(self.crt_total_usage(self.df_system), on="ID", how="left")
        df_user = df_user.merge(self.crt_time_of_day_propotions(self.df_system), on="ID", how="left")
        df_user = df_user.merge(self.crt_day_propotion(self.df_system), on="ID", how="left")

        return(df_user)
        










        