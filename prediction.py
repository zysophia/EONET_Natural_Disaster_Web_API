from sklearn.neighbors import KernelDensity
from datetime import datetime, date, timedelta
from database import fetch_all_dis_as_df
import pandas as pd
import numpy as np

def norm_kde(df_wf,h):
    mean_geo2 = np.mean(df_wf['geo2'])
    mean_geo1 = np.mean(df_wf['geo1'])
    mean_date = np.mean([datetime.fromisoformat(str(df_wf['datetime'].iloc[i])).timestamp() for i in range(len(df_wf))])

    std_geo2 = np.std(df_wf['geo2'])
    std_geo1 = np.std(df_wf['geo1'])
    std_date = np.std([datetime.fromisoformat(str(df_wf['datetime'].iloc[i])).timestamp() for i in range(len(df_wf))])
    X = np.array([ [ (df_wf['geo2'].iloc[i] - mean_geo2)/std_geo2,
                    (df_wf['geo1'].iloc[i] - mean_geo1)/std_geo1,
                    (datetime.fromisoformat(str(df_wf['datetime'].iloc[i])).timestamp()-mean_date)/std_date ] 
                  for i in range(len(df_wf)) ])
    kde = KernelDensity(kernel='gaussian', bandwidth=h).fit(X)
    return kde,(mean_geo2,mean_geo1,mean_date,std_geo2,std_geo1,std_date)

def kde_predict(x,kde):
    a = (x[0]-kde[1][0])/kde[1][3]
    b = (x[1]-kde[1][1])/kde[1][4]
    c = (x[2]-kde[1][2])/kde[1][5]
    return kde[0].score_samples([[a,b,c]])[0]

def kde(df,h,loc):
    df = df[df['title']=='Wildfires']
    kde = norm_kde(df,h)
    dates = []
    for i in range(32):
        d = datetime.now() - timedelta(days=i)
        d = d.timetuple()
        dates.append(date(d[0],d[1],d[2]))
    if loc == 'la':
        kde_pred = [kde_predict(
                        [34,-118,datetime.fromisoformat(str(dates[i])).timestamp()]
                       ,kde
                      ) for i in range(len(dates))]
    elif loc == 'st':
        kde_pred = [kde_predict([47,-122,datetime.fromisoformat(str(dates[i])).timestamp()]
                       ,kde
                      ) for i in range(len(dates))]
    return pd.DataFrame({'date':dates,'kde':kde_pred})

if __name__=='__main__':
    print(kde(fetch_all_dis_as_df(), 0.1, "la"))