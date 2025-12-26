import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# --- 1. DATA GENERATION ---
def generate_survey_data(n=1):
    np.random.seed(None) 
    age_groups = ['Under 18', '18–20', '21–23', '24–26', '27–29']
    genders = ['Male', 'Female', 'Prefer not to say']
    programs = ['Data science', 'Fashion design', 'Arts and Interior Architecture', 'Psychology & Counselling']
    
    new_data = []
    for i in range(n):
        program = np.random.choice(programs)
        # Hidden logic: Higher SM score -> Higher Distraction
        hidden_sm_score = np.random.normal(5, 2.5) 
        
        if hidden_sm_score < 2: sm_choice = 'Less than 1 hour'
        elif hidden_sm_score < 4: sm_choice = '1–2 hours'
        elif hidden_sm_score < 6: sm_choice = '3–4 hours'
        elif hidden_sm_score < 8: sm_choice = '5–6 hours'
        else: sm_choice = 'More than 6 hours'

        if hidden_sm_score > 6: # Heavy user
            distraction = np.random.choice(['Often', 'Always'], p=[0.4, 0.6])
            impact = np.random.choice(['Somewhat Negative', 'Strongly Negative'], p=[0.4, 0.6])
            study_choice = np.random.choice(['Less than 2 hours', '2–4 hours'], p=[0.6, 0.4])
        elif hidden_sm_score < 3: # Light user
            distraction = np.random.choice(['Never', 'Rarely'], p=[0.3, 0.7])
            impact = np.random.choice(['Strongly Positive', 'Somewhat Positive', 'Neutral'], p=[0.2, 0.3, 0.5])
            study_choice = np.random.choice(['5–7 hours', '8+ hours'], p=[0.6, 0.4])
        else: # Average user
            distraction = np.random.choice(['Sometimes', 'Often'], p=[0.7, 0.3])
            impact = np.random.choice(['Neutral', 'Somewhat Negative'], p=[0.7, 0.3])
            study_choice = np.random.choice(['2–4 hours', '5–7 hours'], p=[0.5, 0.5])

        row = {
            'Program_of_Study': program,
            'Average_Daily_SM_Usage': sm_choice,
            'Daily_Study_Work_Hours': study_choice,
            'Distraction_Frequency': distraction,
            'Productivity_Impact': impact,
        }
        new_data.append(row)
    return pd.DataFrame(new_data)

# Mappings for Scatter Plot
sm_map = {'Less than 1 hour': 0.5, '1–2 hours': 1.5, '3–4 hours': 3.5, '5–6 hours': 5.5, 'More than 6 hours': 7}
study_map = {'Less than 2 hours': 1, '2–4 hours': 3, '5–7 hours': 6, '8+ hours': 9}

# Initial Data
df_global = generate_survey_data(100)

# --- 2. DASHBOARD APP ---
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("📱 Social Media & Student Productivity", style={'textAlign': 'center', 'fontFamily': 'Arial'}),

    html.Div([
        html.Label("Filter by Program:"),
        dcc.Dropdown(
            id='program-filter',
            options=[{'label': i, 'value': i} for i in df_global['Program_of_Study'].unique()],
            value='Data science',
            clearable=False  # Fixed: Capitalized False
        ),
    ], style={'width': '50%', 'margin': 'auto'}),

    dcc.Interval(id='interval-component', interval=2000, n_intervals=0),
    html.Div(id='live-stats', style={'textAlign': 'center', 'margin': '20px', 'fontSize': '18px'}),

    html.Div([
        html.Div([dcc.Graph(id='scatter-plot')], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='distraction-bar')], style={'width': '48%', 'display': 'inline-block'}),
    ]),
    html.Div([dcc.Graph(id='impact-pie')], style={'width': '100%', 'display': 'inline-block'}),
])

# --- 3. INTERACTIVITY ---
@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('distraction-bar', 'figure'),
     Output('impact-pie', 'figure'),
     Output('live-stats', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('program-filter', 'value')]
)
def update_dashboard(n, selected_program):
    global df_global
    new_entry = generate_survey_data(1)
    df_global = pd.concat([df_global, new_entry], ignore_index=True)

    filtered_df = df_global[df_global['Program_of_Study'] == selected_program].copy()
    if filtered_df.empty: filtered_df = df_global

    # Scatter Processing
    filtered_df['SM_Numeric'] = filtered_df['Average_Daily_SM_Usage'].map(sm_map)
    filtered_df['Study_Numeric'] = filtered_df['Daily_Study_Work_Hours'].map(study_map)
    # Add Jitter
    filtered_df['SM_Numeric'] += np.random.uniform(-0.3, 0.3, len(filtered_df))
    filtered_df['Study_Numeric'] += np.random.uniform(-0.3, 0.3, len(filtered_df))

    fig1 = px.scatter(filtered_df, x='SM_Numeric', y='Study_Numeric', color='Distraction_Frequency',
                      title=f"Correlation ({selected_program})", 
                      labels={'SM_Numeric': 'Daily SM Hours', 'Study_Numeric': 'Daily Study Hours'})

    counts = filtered_df['Distraction_Frequency'].value_counts().reset_index()
    counts.columns = ['Distraction', 'Count']
    fig2 = px.bar(counts, x='Distraction', y='Count', title="Distraction Frequency")

    fig3 = px.pie(filtered_df, names='Productivity_Impact', title="Perceived Impact")

    return fig1, fig2, fig3, f"Total Responses: {len(df_global)}"

# --- 4. RUN SERVER ---
if __name__ == '__main__':
    print("✅ Dashboard is ready! Open this link in your browser:")
    print("http://127.0.0.1:8050/")
    print("-----------------------------------------------------")
    
    # Run the app
    app.run(debug=True, use_reloader=False)