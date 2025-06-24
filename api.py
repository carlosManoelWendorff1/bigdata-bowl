import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
from fastapi import FastAPI

def generate_sample_tracking_data(num_players=10, num_games=5, fps=10, duration_min=60):
    np.random.seed(42)
    players = [f'P{1000+i}' for i in range(num_players)]
    games = [f'G{2000+i}' for i in range(num_games)]
    all_data = []
    field_length, field_width = 120, 53.3
    
    for game in games:
        start_time = datetime(2023, 9, 1, 13, 0, 0)
        frame_times = pd.date_range(start_time, periods=fps*duration_min*60, freq=f'{1/fps}S')
        
        for player in players:
            x_start, y_start = np.random.uniform(0, field_length), np.random.uniform(0, field_width)
            dx = np.cumsum(np.random.normal(0, 0.5, len(frame_times)))
            dy = np.cumsum(np.random.normal(0, 0.3, len(frame_times)))
            
            player_data = pd.DataFrame({
                'time': frame_times,
                'game': game,
                'player': player,
                'x': np.clip(x_start + dx, 0, field_length),
                'y': np.clip(y_start + dy, 0, field_width),
                'dir': np.random.uniform(0, 360, len(frame_times)),
                'speed': 0,
                'acceleration': 0
            })
            all_data.append(player_data)
    
    return pd.concat(all_data).sort_values(['game', 'player', 'time'])

def generate_sample_injury_data(tracking_data, injury_rate=0.05):
    injuries = tracking_data[['player', 'game']].drop_duplicates()
    injuries['injury'] = np.random.choice([0, 1], size=len(injuries), p=[1-injury_rate, injury_rate])
    return injuries[injuries['injury'] == 1]

def calculate_movement_metrics(tracking_data):
    tracking_data = tracking_data.sort_values(['player', 'time'])
    tracking_data['dt'] = tracking_data.groupby('player')['time'].diff().dt.total_seconds().replace(0, 0.1)
    tracking_data['dx'] = tracking_data.groupby('player')['x'].diff()
    tracking_data['dy'] = tracking_data.groupby('player')['y'].diff()
    tracking_data['speed'] = np.sqrt(tracking_data['dx']**2 + tracking_data['dy']**2) / tracking_data['dt']
    tracking_data['acceleration'] = tracking_data.groupby('player')['speed'].diff() / tracking_data['dt']
    tracking_data['direction_change'] = tracking_data.groupby('player')['dir'].diff().abs()
    tracking_data['direction_change'] = tracking_data['direction_change'].apply(lambda x: min(x, 360-x) if pd.notna(x) else 0)
    return tracking_data[~tracking_data['dt'].isna()]

def aggregate_player_stats(tracking_data, window='1min'):
    grouped = tracking_data.groupby(['player', 'game', pd.Grouper(key='time', freq=window)])
    agg_stats = grouped.agg({
        'speed': ['mean', 'max', 'std'],
        'acceleration': ['mean', 'max', 'std'],
        'direction_change': ['mean', 'max', 'sum']
    })
    agg_stats.columns = ['_'.join(col).strip() for col in agg_stats.columns.values]
    return agg_stats.reset_index()

def prepare_model_data(agg_stats, injury_data):
    model_data = pd.merge(agg_stats, injury_data, on=['player', 'game'], how='left')
    model_data['injury'] = model_data['injury'].fillna(0)
    model_data['future_injury'] = model_data.groupby(['player', 'game'])['injury'].shift(-3)
    return model_data[~model_data['future_injury'].isna()]

def train_injury_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()
    X_train = scaler.fit_transform(imputer.fit_transform(X_train))
    X_test = scaler.transform(imputer.transform(X_test))
    
    model = RandomForestClassifier(n_estimators=100, max_depth=5, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    print(classification_report(y_test, y_pred))
    print(f"AUC-ROC: {roc_auc_score(y_test, y_proba):.3f}")
    return model, scaler, imputer

def analyze_player(player_data, model, scaler, imputer):
    try:
        player_data = player_data.sort_values('time').drop_duplicates('time')
        features = player_data[['speed_mean', 'acceleration_max', 'direction_change_sum']]
        features_clean = features.replace([np.inf, -np.inf], np.nan).fillna(features.median())
        
        player_data['injury_prob'] = model.predict_proba(
            scaler.transform(imputer.transform(features_clean)))[:, 1]
        
        mean_risk = player_data['injury_prob'].mean()

        return {"player_time": player_data['time'], "injury_prob": player_data['injury_prob'], "mean_risk": mean_risk}
        
    except Exception as e:
        print(f"Erro ao analisar jogador: {str(e)}")

pd.set_option('display.max_columns', 500)
plt.style.use('ggplot')

print("Gerando dados simulados...")
tracking_data = generate_sample_tracking_data(num_players=20, num_games=3)
injury_data = generate_sample_injury_data(tracking_data)

print("\nCalculando métricas de movimento...")
tracking_metrics = calculate_movement_metrics(tracking_data)
agg_stats = aggregate_player_stats(tracking_metrics)
model_data = prepare_model_data(agg_stats, injury_data)

print("\nTreinando modelo...")
features = model_data[['speed_mean', 'acceleration_max', 'direction_change_sum']]
target = model_data['future_injury']
model, scaler, imputer = train_injury_model(features, target)

app = FastAPI()

@app.get("/analize")
async def root():
    print("\nAnalisando jogadores...")
    for player in model_data['player'].unique()[:3]:
        player_data = model_data[model_data['player'] == player]
        return analyze_player(player_data, model, scaler, imputer)
