import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo '{file_path}'.")
        return pd.DataFrame()

    df['date_game'] = pd.to_datetime(df['date_game'])
    df = df[df['game_result'].isin(['W', 'L'])]
    
    return df

df = load_data("nba_all_elo.csv")

if df.empty:
    st.stop()

# Barra lateral
st.sidebar.header("Filtros del dashboard")

# Selección de año
season_list = df['year_id'].unique()
season_list.sort()

# Selección de equipo
team_list = df['team_id'].unique()
team_list.sort()

# Selección de temporada
selected_season = st.sidebar.selectbox(
    'Seleccionar año (Temporada):',
    season_list,
    index=len(season_list) - 1 
)

# Selección de equipo
selected_team = st.sidebar.selectbox(
    'Seleccionar equipo:',
    team_list,
    index=list(team_list).index('NYK') if 'NYK' in team_list else 0
)

# Selección de tipo de juego
game_type = st.sidebar.radio(
    'Seleccionar el tipo de juego:',
    ['Temporada regular', 'Playoffs', 'Ambos'],
    horizontal=True 
)


df_filtered = df[
    (df['year_id'] == selected_season) &
    (df['team_id'] == selected_team)
]

if game_type == 'Temporada regular':
    df_filtered = df_filtered[df_filtered['is_playoffs'] == 0]
elif game_type == 'Playoffs':
    df_filtered = df_filtered[df_filtered['is_playoffs'] == 1]

df_filtered = df_filtered.sort_values('date_game')

if df_filtered.empty:
    st.warning(f"No se encontraron datos para {selected_team} en el año {selected_season} con el filtro '{game_type}'.")
else:
    df_filtered['win'] = (df_filtered['game_result'] == 'W').astype(int)
    df_filtered['loss'] = (df_filtered['game_result'] == 'L').astype(int)
    
    # Calcular el acumulado (cumulative sum)
    df_filtered['cumulative_wins'] = df_filtered['win'].cumsum()
    df_filtered['cumulative_losses'] = df_filtered['loss'].cumsum()
    
    pie_colors= ["#F43636", "#28F321"]
    line_colors = ["#F43636", "#28F321"]

   
    df_line_chart = df_filtered.set_index('date_game')[['cumulative_wins', 'cumulative_losses']]
    
    df_line_chart = df_line_chart.rename(columns={
        'cumulative_wins': 'Ganados (W)',
        'cumulative_losses': 'Perdidos (L)'
    })

    total_wins = df_filtered['win'].sum()
    total_losses = df_filtered['loss'].sum()
    pie_data = [total_wins, total_losses]
    pie_labels = [f'Ganados (W): {total_wins}', f'Perdidos (L): {total_losses}']


    st.title(f"Dashboard NBA: {selected_team}")
    st.header(f"Año: {selected_season} | Tipo: {game_type}")
    
    col1, col2 = st.columns([2, 1]) 

    with col1:
        st.subheader("Juegos ganados y perdidos acumulados")
        
        st.line_chart(
            df_line_chart,
            color=line_colors,
            use_container_width=True
        )

    with col2:
        st.subheader("Porcentaje de victorias y derrotas")
        
        fig_pie, ax2 = plt.subplots(figsize=(8, 6))
        
        if total_wins == 0 and total_losses == 0:
            ax2.text(0.5, 0.5, 'Sin datos', horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title("Total de juegos: 0", pad=20)
        else:
            wedges, texts, autotexts = ax2.pie(
                pie_data, 
                labels=pie_labels, 
                autopct='%1.1f%%', 
                startangle=90, 
                colors=pie_colors,
                pctdistance=0.85,
                textprops={'color': 'black', 'fontsize': 10}
            )
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig_pie.gca().add_artist(centre_circle)
            plt.setp(autotexts, size=12, weight="bold", color="white")
            
        ax2.set_title(f"Total de juegos: {total_wins + total_losses}", pad=20)
        ax2.axis('equal')  
        
        st.pyplot(fig_pie)
