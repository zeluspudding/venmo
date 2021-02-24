import pandas as pd
import os

script_dir = os.path.abspath('')
project_dir =  os.path.dirname(os.path.abspath(''))
data_dir = os.path.join(project_dir, 'references')

file_path = os.path.join(data_dir, 'cost_table.csv')

df_cost_table = pd.read_csv(file_path)

players = {
    1:
        {"players_name": "OLIVIA", "balance": 1500, "properties":[]},
    2:
        {"players_name": "ELIZABETH", "balance": 1500, "properties":[]},
    3:
        {"players_name": "JUSTIN", "balance": 1500, "properties":[]},
    4:
        {"players_name": "CHARLIE", "balance": 1500, "properties":[]},
    }
total_turns = 154
winner_net_worth = 9560

dfs = []
columns = ['date','name','value', 'category']

def who_owns_property(property_id, players):
    for player in players.items():
        players_name = player[1]['players_name']
        players_property = player[1]['properties']
        if property_id in players_property:
            return player[0]
    return None

def get_weighted_housing_prices(turn):
    # defining the probability of charging rents
    # 'Base Rent', '1 house rent', '2 house rent', '3 house rent','4 house rent', 'hotel rent'
    if turn < 0.3 * total_turns:
        return [0.95, 0.05, 0, 0, 0, 0]
    elif turn < 0.6 * total_turns:
        return [0.2, 0.4, 0.3, 0.1, 0, 0]
    elif turn < 0.9 * total_turns:
        return [0, 0, 0.2, 0.4, 0.3, 0.1]
    else:
        return [0, 0, 0.1, 0.35, 0.35, 0.2]

for turn in range(total_turns):
    date = pd.Timestamp(year=1990 + turn, month=1, day=1).strftime("%Y-%m-%d")
    for player in players.items():
        players_name = player[1]['players_name']
        players_current_balance = player[1]['balance']
        players_property = player[1]['properties']
        if turn != 0:
            
            df_landed_property = df_cost_table.sample(1, weights='weights',axis=0)
            location_id = int(df_landed_property['Location'])
            if location_id in players_property:
                continue
                # new_balance = players_current_balance
            else:
                property_owner = who_owns_property(location_id, players)
                if property_owner is not None:
                    weights = get_weighted_housing_prices(turn)
                    payment = int(df_landed_property[['Base Rent', '1 house rent', '2 house rent', '3 house rent','4 house rent', 'hotel rent']].sample(weights = weights, axis=1).iloc[0])
                    players[player[0]]['balance'] = players_current_balance - payment
                    players[property_owner]['balance'] = int(players[property_owner]['balance']) + payment
                    
                else: #No one owns this property
                    property_cost = int(df_landed_property['Cost'])
                    if players_current_balance > property_cost:
                        players[player[0]]['balance'] = players_current_balance - property_cost
                        players[player[0]]['properties'].append(location_id)
            
            dfs.append(pd.DataFrame([[date,players_name,int(players[player[0]]['balance']),players_name]], columns= columns))
        else:
            dfs.append(pd.DataFrame([[date,players_name,players_current_balance,players_name]], columns= columns))
    
df = pd.concat(dfs)
#%%
df.loc[df['value'] < 0,'value'] = 0
df.to_csv(os.path.join(data_dir, 'bar_chart_race_data.csv'),index=False)