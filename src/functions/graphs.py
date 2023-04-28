import plotly.express as px
import pandas as pd

theme = 'none'


def create_radar_plot(df):
    
    df_features = df.groupby(['label', 'algorithm']).agg({
                # 'popularity': 'mean',
                'acousticness': 'mean',
                'danceability': 'mean',
                'energy': 'mean',
                'instrumentalness': 'mean',
                # 'loudness': 'mean',
                'liveness': 'mean',
                'speechiness': 'mean',
                'valence': 'mean',
                # 'tempo': 'mean',
            }).reset_index()
    
    df_features = pd.melt(df_features, id_vars=['label', 'algorithm'], value_vars=['acousticness',
                                                                                  'danceability',
                                                                                  'energy',
                                                                                  'instrumentalness',
                                                                                  'liveness',
                                                                                  'speechiness',
                                                                                  'valence'] )
    
    fig = px.line_polar(df_features, 
                        r='value',
                        theta='variable',
                        color='label',
                        line_close=True,
                        template=theme)
    fig.update_traces(fill='toself')
    
    return fig

def create_year_plot(df):
    
    df['release_year'] = df['release_date'].apply(lambda x: int(x.split('-')[0]))
    
    fig = px.strip(df, 
                    x="release_year", 
                    y="label", 
                    color="label", 
                    template=theme,
                    hover_data=['name','album','artist'],
                    )
    
    fig.update_layout(showlegend=False)

    return fig


def create_key_mode_plot(df):
    
    df_g = df.groupby(['label', 'key']).size().reset_index()
    df_g.columns = ['label', 'key', 'count']

    keys_map = {
        0: 'C',
        1: 'C#',
        2: 'D',
        3: 'D#',
        4: 'E',
        5: 'F',
        6: 'F#',
        7: 'G',
        8: 'G#',
        9: 'A',
        10: 'A#',
        11: 'B',
    }

    df_g['key'] = df_g['key'].apply(lambda x: keys_map[x])

    df_keys = pd.DataFrame(['C','C#','D','D#','E','F','F#','G','G#','A', 'A#', 'B'], columns=['key'])

    df_final = None
    
    for x in df_g.label.unique():

        df_tmp = pd.merge(left=df_keys, 
                right=df_g.loc[df_g['label'] == x, ['label', 'key', 'count']].sort_values(by='count', ascending=False),
                on='key',
                how='left')
        df_tmp['label'].fillna(x, inplace=True)
        df_tmp['count'].fillna(0, inplace=True)
        
        if df_final is None:
            df_final = df_tmp
        else:
            df_final = pd.concat([df_final, df_tmp])
    
    fig = px.bar(df_final, 
                 x="key", 
                 y="count",
                 color="label",
                 barmode='group',
                 template=theme)   
        
    return fig


def create_tempo_plot(df):
    
    fig = px.violin(df, 
                    x="label", 
                    y="tempo",
                    color="label",
                    hover_data=['name','album','artist','release_date'],
                    template=theme,
                    )
    
    fig.update_layout(showlegend=False)

    return fig


def create_line_plot_df_exec(pl_recsys_data, x, color):
    
    df_exec = pl_recsys_data.df_exec
    
    fig = px.line(df_exec, 
                  x= x,
                  y= 'exec_time', 
                  color=color,
                  markers=True,
                  template=theme,
                  hover_data=df_exec.columns)
    
    return fig

def create_dispersion_plot(df,x):
    
    fig = px.strip(df, 
                   y=x, 
                   x="label", 
                   color="label", 
                   template=theme,
                   hover_data=['name','album','artist','release_date'],)
    
    return fig
    