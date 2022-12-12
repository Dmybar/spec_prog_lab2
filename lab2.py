from spyre import server

import pandas as pd
import datetime

areas=[1,2,3,4,5,6,7,8,9,10,11,13,14,15,15,17,18,19,21,22,23,24,26,27]

df = pd.DataFrame()

path='UkrVHI_csv/'
UkrVHI_files = pd.read_csv(path+'info.csv',index_col=0)
name_columns = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI']

for index in UkrVHI_files.index:
    temp = pd.read_csv(path+UkrVHI_files['file_name'][index],header=1,index_col=False,names=name_columns)
    temp = temp.assign(Area=UkrVHI_files['index_area'][index]) 
    df = pd.concat([df,temp],ignore_index=True)

df = df.dropna()
df = df.drop(df.loc[df['VHI']==-1].index)
df['Year']=df['Year'].replace(['<tt><pre>1982'],'1982')
df = df.astype({'Week':'int','Year':'int'})

class StockExample(server.App):
    title = "NOAA data vizualization"

    inputs = [{     "type":'dropdown',
                    "label": 'NOAA data dropdown',
                    "options" : [ {"label": "VCI", "value":"VCI"},
                                  {"label": "TCI", "value":"TCI"},
                                  {"label": "VHI", "value":"VHI"}],
                    "key": 'ticker1',
                    "action_id": "update_data"},
              {     "type":'dropdown',
                    "label": 'Area',
                    "options" : [dict(label=i,value=i) for i in areas],
                    "key": 'ticker2',
                    "action_id": "update_data"},
              {     "type":'text',
                    "label": 'date-ranges',
                    "value":"9-10",
                    "key": 'range_week',
                    "action_id": "simple_html_output"}]

    controls = [{   "type" : "hidden",
                    "id" : "update_data"}]

    tabs = ["Plot", "Table"]

    outputs = [{ "type" : "plot",
                    "id" : "plot",
                    "control_id" : "update_data",
                    "tab" : "Plot"},
               {  "type" : "table",
                    "id" : "table_id",
                    "control_id" : "update_data",
                    "tab" : "Table",
                    "on_page_load" : True },
               {  "type":'html',
                    "id":'simple_html_output'}]
    def getHTML(self, params):
        range_week = params["range_week"]
        return range_week
    
    def getData(self, params):
        ticker1 = params['ticker1']
        ticker2 = params['ticker2']
        weeks = params['range_week']        
        
        week_min = int(weeks[:weeks.find('-')])
        week_max = int(weeks[(weeks.find('-')+1):])
        
        return df.loc[(df['Area']==int(ticker2))&(df['Week']>=week_min)&(df['Week']<=week_max)][['Year','Week',ticker1]]
    
    def getPlot(self, params):
        ticker1 = params['ticker1']
        df_pl = self.getData(params)
        df_pl = df_pl.assign(Date=[datetime.date.fromisocalendar(df_pl['Year'][i],df_pl['Week'][i],1) for i in df_pl.index])
        df_pl = df_pl.set_index('Date').drop(['Year','Week'],axis=1)
        plt_obj = df_pl.plot(figsize=(18,10))
        fig = plt_obj.get_figure()
        return fig
    
app = StockExample()
app.launch(port=9092)