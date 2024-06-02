import numpy as np
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
        
    def crt_user_features(self):
        """
        """
        df_user = self.df_system.loc[:,["ID"]].drop_duplicates()
        df_user = df_user.merge(self.df_system.loc[:,["ID", "place of residence"]].drop_duplicates(), on="ID", how="left")
        df_user = df_user.merge(self.crt_user_type(self.df_system), on="ID", how="left")

        return(df_user)
        










        