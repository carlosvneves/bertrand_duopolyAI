import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os

import datetime
import time

from sabm.arguments import argparser
import sabm.pricing_competition as competition
from dotenv import load_dotenv
import os

from sabm.pricing_competition import model_backend

load_dotenv()

try:
    # api_key = os.environ["OPENAI_API_KEY"]
    api_key1 = os.environ["MARITACA_API_KEY_AG1"]
    api_key2 = os.environ["MARITACA_API_KEY_AG2"]
except:
    api_key = open("apikey.token").readline().strip()


st.set_page_config(
    page_title="Pricing Competition Dashboard",
    page_icon="📊",
    layout="wide"
)


def create_time_series_plot(df, y_column, title):
    fig = go.Figure()

    # Add traces for each firm
    for firm_id in [1, 2]:
        firm_data = df[df['FirmID'] == firm_id]
        fig.add_trace(
            go.Scatter(
                x=firm_data['Round'],
                y=firm_data[y_column],
                name=f'Firm {firm_id}',
                line=dict(
                    color='#FF6103' if firm_id == 1 else '#1C86EE'
                )
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Round",
        yaxis_title=y_column,
        hovermode='x unified',
        showlegend=True,
        template='plotly_white',
        height=400
    )

    return fig


def load_data(output_path):
    decision_plot_path = os.path.join(output_path, "logs_decision_plot.csv")
    conversation_path = os.path.join(output_path, "logs_conversation.txt")

    data = None
    logs = None

    if os.path.exists(decision_plot_path):
        data = pd.read_csv(decision_plot_path)

    if os.path.exists(conversation_path):
        with open(conversation_path, 'r') as f:
            logs = f.read()

    return data, logs


def main(args):
    st.title("Pricing Competition Dashboard")
    # Initialize session state for auto-refresh
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True

    # Model and language settings
    model_backend = 'OnlineMaritacaAI'
    model_version = 'Sabia3_small'
    prompt_language = 'pt_br'

    # Simulation parameters
    rounds = 500
    output_max_tokens = 128
    breakpoint_rounds = 10
    persona_firm1 = 1
    persona_firm2 = 1
    set_initial_price = 'store_true'

    # Cost and economic parameters
    cost = [2, 2]
    parameter_a = 14
    parameter_d = 0.00333333333333
    parameter_beta = 0.00666666666666
    initial_price = [2, 2]
    load_data_location = ''

    # Strategy settings
    strategy = True
    has_conversation = False

    competition.my_apikey1 = api_key1
    competition.my_apikey2 = api_key2
    competition.model_backend = model_backend
    competition.model_ver = model_version
    competition.prompt_language = prompt_language
    competition.rounds = rounds
    competition.output_max_tokens = output_max_tokens
    competition.breakpoint_rounds = breakpoint_rounds
    competition.firm_persona_1 = persona_firm1
    competition.firm_persona_2 = persona_firm2
    competition.program_run_dict["Set_Initial_Prices"] = set_initial_price

    # Configuration
    program_run_dict = {
        "DA": True,
        "Set_Initial_Prices": True,
        "Conversation": False,
    }

    if button_clicked := st.button("Run Simulation"):
        # System Setup
        output_path = f"output/pricing_competition/Record-{datetime.date.today().strftime('%y%m%d')}-{time.strftime('%H%M')}-{model_version}-{prompt_language}"
        os.makedirs(output_path, exist_ok=True)

        competition.run_simulation(
            cost,
            parameter_a,
            parameter_d,
            parameter_beta,
            initial_price,
            load_data_location,
            strategy,
            has_conversation,
            output_path,
        )


    # Sidebar
    st.sidebar.title("Settings")
    output_path = st.sidebar.text_input(
        "Output Directory",
        #value="output/pricing_competition/",
        value = output_path,
        help="Path to the simulation output directory"
    )

    update_interval = st.sidebar.slider(
        "Update Interval (seconds)",
        min_value=1,
        max_value=30,
        value=5
    )

    st.session_state.auto_refresh = st.sidebar.checkbox(
        "Auto Refresh",
        value=st.session_state.auto_refresh
    )

    if st.session_state.auto_refresh:
        st.empty()
        time.sleep(update_interval)
        st.rerun()

    # Create layout
    col1, col2 = st.columns(2)

    # Load data
    data, logs = load_data(output_path)

    # Display logs
    with col1:
        st.subheader("Simulation Logs")
        if logs is not None:
            st.text_area(
                "Latest logs",
                value=logs,
                height=800,
                key="logs"
            )
        else:
            st.warning("No logs available")

    # Display plots
    with col2:
        st.subheader("Real-time Plots")
        if data is not None:
            st.plotly_chart(
                create_time_series_plot(data, 'Price', 'Price Evolution'),
                use_container_width=True
            )
            st.plotly_chart(
                create_time_series_plot(data, 'Quantity', 'Quantity Evolution'),
                use_container_width=True
            )
            st.plotly_chart(
                create_time_series_plot(data, 'Profit', 'Profit Evolution'),
                use_container_width=True
            )
        else:
            st.warning("Waiting for simulation data...")

    # Add refresh button for manual refresh
    if not st.session_state.auto_refresh:
        if st.button("Refresh Data"):
            st.rerun()



# def main(args):
#     competition.my_apikey1 = api_key1
#     competition.my_apikey2 = api_key2
#     competition.model_backend = args.model_backend
#     competition.model_ver = args.model_version
#     competition.prompt_language = args.prompt_language
#     competition.rounds = args.rounds
#     competition.output_max_tokens = args.output_max_tokens
#     competition.breakpoint_rounds = args.breakpoint_rounds
#     competition.firm_persona_1 = args.persona_firm1
#     competition.firm_persona_2 = args.persona_firm2
#     competition.program_run_dict["Set_Initial_Prices"] = args.set_initial_price
#
#     model_ver = competition.model_ver
#     prompt_language = competition.prompt_language
#
#     # System Setup
#     output_path = f"output/pricing_competition/Record-{datetime.date.today().strftime('%y%m%d')}-{time.strftime('%H%M')}-{model_ver}-{prompt_language}"
#     os.makedirs(output_path, exist_ok=True)
#
#     competition.run_simulation(
#         args.cost,
#         args.parameter_a,
#         args.parameter_d,
#         args.parameter_beta,
#         args.initial_price,
#         args.load_data_location,
#         args.strategy,
#         args.has_conversation,
#         output_path,
#     )




