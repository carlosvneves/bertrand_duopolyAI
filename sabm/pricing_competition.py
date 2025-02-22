import pandas as pd
import matplotlib.pyplot as plt
import random
import os
import datetime
import time
import csv
import ast
from dotenv import load_dotenv


import sabm.agent as GPT
# import src.firm_pricing_competition.prompt as Data
# import src.firm_pricing_competition.prompt_pt_br_enhanced as Data
import sabm.prompt_pt_br as Data_br
import sabm.prompt_pt_br_enhanced as Data_br_enh
import sabm.prompt as Data_en 
import sabm.data_theoretical_solution as data_theoretical_solution
import sabm.data_plot as data_plot
import sabm.data_output as data_output

from sabm.utils import ModelType, BackendType


load_dotenv()
plt.ion()

# model defaults
model_backend="OnlineMaritacaAI"
model_ver = "Sabia3_small" # LLM here, e.g., "sabia-3"

# API Keys
my_apikey1 = ""
my_apikey2 = ""

if model_backend == BackendType.OnlineGroq.value:
    my_apikey1 = os.getenv("GROQ_API_KEY") # GROQ API key here for firm 1
    my_apikey2 = os.getenv("GROQ_API_KEY") # GROQ API key here for firm 2
elif model_backend == BackendType.OnlineMistral.value:
    my_apikey1 = os.getenv("MISTRAL_API_KEY") # MISTRAL API key here for firm 1
    my_apikey2 = os.getenv("MISTRAL_API_KEY") # MISTRAL API key here for firm 2
elif model_backend == BackendType.OnlineGoogle.value:
    my_apikey1 = os.getenv("GOOGLE_API_KEY") # GOOGLE API key here for firm 1
    my_apikey2 = os.getenv("GOOGLE_API_KEY") # GOOGLE API key here for firm 2
else:
    my_apikey1 = os.getenv("MARITACA_API_KEY_AG1") # MARITACA API key here for firm 1
    my_apikey2 = os.getenv("MARITACA_API_KEY_AG2") # MARITACA API key here for firm 2

    
# Configuration
program_run_dict = {
    "DA": True,
    "Set_Initial_Prices": True,
    "Conversation": False,
}
## Round Setup
rounds = 100000
n_communications_noconversation = 1
n_communications_conversation = 3
output_max_tokens = 128
breakpoint_rounds = 200
prev_n_rounds = 20
## Agent Persona
firm_persona_1 = '1' # Firm 1 persona (0: None, 1: Active, 2: Aggressive)
firm_persona_2 = '1' # Firm 2 persona (0: None, 1: Active, 2: Aggressive)

# Prompt
prompt_language = "pt_br"
Data = Data_br_enh
# Model
prompts = Data.prompts
persona_prompts = Data.persona
log_format = Data.log_format

def round_function(x: float):
    return round(x, 3)

class Market:
    def __init__(self, firms, rounds = 1000, n_communications = 3):
        self.firms = firms
        self.rounds = rounds
        self.n_communications = n_communications

    
    def firm_name(self, ids):

        return Data.name_dict.get(ids)

    def simulate(self, ideal_solution, initial_price = [0, 0], breakpoint_rounds = 0, output_path = "", current_round = 0):
        logs_conversation = []
        log_price_data = []
        log_price_data_plot = []
        log_strategy = []

        # Output initial settings
        log_settings = "Initial Settings:\n"
        for firm in self.firms:
            log_settings += f"Firm {firm.id}: cost = {firm.cost}, a = {firm.a}, d = {firm.d}, temp = {firm.temperature}\n"

        # Main Loop
        for round in range(current_round, self.rounds):
            print(f"Round #{round + 1}:")
            
            # Breakpoint
            if breakpoint_rounds != 0:
                if (round + 1) % breakpoint_rounds == 0:
                    breakpoint_key = str(input("Continue? (Y/N) "))
                    if breakpoint_key[0] == 'N' or breakpoint_key[0] == 'n': break
            
            #################################
            # Phase 1: Firms communicate
            # Shuffle the firms' order
            random.shuffle(self.firms)

            prices = []
            logs_round = []
            decision_log = ""
            conversation = ""
            context_game_description = ""

            for firm in self.firms:
                # Game instructions
                if program_run_dict.get("Conversation") == False:
                    if firm.id == 1:
                        context_game_description = prompts["game_description"].format(firm_name = firm.firm_name, firm_name_2 = self.firm_name(firm.id % len(self.firms) + 1), firm_cost = firm.cost, v1 = (1 / (1 - firm.d * firm.d)), v2 = (firm.a - firm.a * firm.d), v3 = firm.d, persona = persona_prompts["firm_persona_{}".format(firm_persona_1)])
                    if firm.id == 2:
                        context_game_description = prompts["game_description"].format(firm_name = firm.firm_name, firm_name_2 = self.firm_name(firm.id % len(self.firms) + 1), firm_cost = firm.cost, v1 = (1 / (1 - firm.d * firm.d)), v2 = (firm.a - firm.a * firm.d), v3 = firm.d, persona = persona_prompts["firm_persona_{}".format(firm_persona_2)])
                else:
                    if firm.id == 1:
                        context_game_description = prompts["game_description_conversation"].format(firm_name = firm.firm_name, firm_name_2 = self.firm_name(firm.id % len(self.firms) + 1), firm_cost = firm.cost, v1 = (1 / (1 - firm.d * firm.d)), v2 = (firm.a - firm.a * firm.d), v3 = firm.d, persona = persona_prompts["firm_persona_{}".format(firm_persona_1)])
                    if firm.id == 2:
                        context_game_description = prompts["game_description_conversation"].format(firm_name = firm.firm_name, firm_name_2 = self.firm_name(firm.id % len(self.firms) + 1), firm_cost = firm.cost, v1 = (1 / (1 - firm.d * firm.d)), v2 = (firm.a - firm.a * firm.d), v3 = firm.d, persona = persona_prompts["firm_persona_{}".format(firm_persona_2)])
                
                context_phase_1 = prompts["Phase_1_Description_1"].format(firm_name = firm.firm_name, round_id = round + 1, firm_price = firm.price, firm_profit = firm.profit)

                # Load previous decisions
                context_past_decisions = ""
                for i in range(max(0, round - prev_n_rounds), round):
                    context_past_decisions += f"Round #{i + 1}: [{firm.price_history[i]}, {round_function(firm.demand_history[i])}, {round_function(firm.profit_history[i])}, {firm.rival_price_history[i]}]\n"
                
                context_prev_consideration = ""
                if round != 0:
                    if round >= prev_n_rounds and round % prev_n_rounds == 0:
                        context_prev_consideration += prompts["Phase_1_Prev_Statistics_Introduction"]

                        for id in range(max(0, int(round / prev_n_rounds) - prev_n_rounds), int(round / prev_n_rounds)):
                            round_lb = id * prev_n_rounds + 1
                            round_rb = (id + 1) * prev_n_rounds
                            context_prev_consideration += prompts["Phase_1_Prev_Statistics"].format(
                                r1=round_lb,
                                r2=round_rb,
                                v1=round_function(float(sum(firm.price_history[round_lb - 1 : round_rb]))/len(firm.price_history[round_lb - 1 : round_rb])),
                                v2=round_function(float(sum(firm.demand_history[round_lb - 1 : round_rb]))/len(firm.demand_history[round_lb - 1 : round_rb])),
                                v3=round_function(float(sum(firm.profit_history[round_lb - 1 : round_rb]))/len(firm.profit_history[round_lb - 1 : round_rb])),
                                v4=round_function(float(sum(firm.rival_price_history[round_lb - 1 : round_rb]))/len(firm.rival_price_history[round_lb - 1 : round_rb])))
                            
                        context_prev_consideration += '\n'
                    
                    context_prev_consideration += prompts["Phase_1_Prev_Decisions_Introduction"].format(prev_round_number = len(range(max(0, round - prev_n_rounds), round)), prev_decisions = context_past_decisions)

                firm.context["context_game_description"] = context_game_description
                firm.context["context_phase_1"] = context_phase_1
                firm.context["context_prev_consideration"] = context_prev_consideration
            
            if program_run_dict.get("Conversation"):
                print("=== Conversation Phase ===")
                for _ in range(self.n_communications):
                    for firm in self.firms:
                        context = firm.context["context_game_description"] + firm.context["context_prev_consideration"]
                        if len(firm.strategy) > 0:
                            context += "Your strategy in " + firm.strategy[-1]
                        context += firm.context["context_phase_1"] + prompts["Phase_1_Description_1_Conversation"]
                        if conversation != "":
                            context += prompts["Load_Conversation_Phase_1"].format(conversations = conversation)
                        #print(context)
                        
                        # response = firm.communicate(context)
                        response = firm.generate_response(context)
                        conversation += log_format["Phase_1_Conversation_Format"].format(firm_name = firm.firm_name, responses = response)
                
                # Logs
                print(conversation)
                logs_round.append(log_format["Phase_1_Log_Format"].format(conversations = conversation))
            
            #################################
            # Phase 2: Firms choose prices
            print("=== Decision Phase ===")
            for firm in self.firms:
                context = ""
                print(f"Firm {firm.firm_name}: Profit {firm.max_profit} with price {firm.max_price} with opponent's price {firm.max_rival_price}")
                
                if round >= prev_n_rounds and round % prev_n_rounds == 0:
                    context_strategy = prompts["Phase_2_Strategy"]
                    for strategy_id in range(max(0, len(firm.strategy) - prev_n_rounds), len(firm.strategy)):
                        context_strategy += firm.strategy[strategy_id]
                    if program_run_dict.get("Conversation") == False:
                        context = firm.context["context_game_description"] + firm.context["context_prev_consideration"] + firm.context["context_phase_1"] + context_strategy + prompts["Reflection_on_Strategy"]
                    else:
                        context_game_description = prompts["game_description"].format(firm_name = firm.firm_name, firm_name_2 = self.firm_name(firm.id % len(self.firms) + 1), firm_cost = firm.cost, v1 = (1 / (1 - firm.d * firm.d)), v2 = (firm.a - firm.a * firm.d), v3 = firm.d, persona = persona_prompts["firm_persona_{}".format(firm_persona_1)])
                        context = context_game_description + firm.context["context_prev_consideration"] + firm.context["context_phase_1"] + context_strategy + prompts["Reflection_on_Strategy"]
                    print(context)
                    #response = firm.communicate(context)
                    response = firm.generate_response(context)
                    firm.strategy.append(f"Round #{round + 1}: ```{response}```\n")
                    print(firm.strategy[-1])
                
                # Price instructions
                context_price_instructions = prompts["Phase_2_Description_1"].format(firm_a = firm.a) 
                
                # Agent make decisions
                if program_run_dict.get("Conversation") == False:
                    if round < prev_n_rounds:
                        context = firm.context["context_game_description"] + firm.context["context_prev_consideration"] + firm.context["context_phase_1"] + context_price_instructions
                    else:
                        context_strategy = prompts["Phase_2_Strategy"]
                        if len(firm.strategy) > 0: context_strategy += firm.strategy[-1]
                        context += firm.context["context_game_description"] + firm.context["context_prev_consideration"] + context_strategy + firm.context["context_phase_1"] + context_price_instructions
                else:
                    context_conversation = prompts["Load_Conversation"].format(conversations = conversation)
                    if round < prev_n_rounds:
                        context = firm.context["context_game_description"] + firm.context["context_prev_consideration"] + firm.context["context_phase_1"] + context_conversation + "We are currently in Phase 2. " + context_price_instructions
                    else:
                        context_strategy = prompts["Phase_2_Strategy"]
                        if len(firm.strategy) > 0: context_strategy += firm.strategy[-1]
                        context += firm.context["context_game_description"] + firm.context["context_prev_consideration"] + context_strategy + firm.context["context_phase_1"] + context_conversation + "We are currently in Phase 2. " + context_price_instructions
                #print(context)
                price, dec_log = firm.choose_price(context)
                
                if program_run_dict.get("Set_Initial_Prices"):
                    if round != 0:
                        prices.append(price)
                    # Set the price interval in the first round
                    else:
                        if firm.id == 1:
                            firm.price = initial_price[0]
                            prices.append(initial_price[0])
                        elif firm.id == 2:
                            firm.price = initial_price[1]
                            prices.append(initial_price[1])
                else:
                    prices.append(price)
                
                # Logs
                decision_log = f"Firm {firm.firm_name}: {dec_log}"
                print(f"Firm {firm.firm_name}: {price}")

                logs_round.append(log_format["Phase_2_Log_Format"].format(firm_name = firm.firm_name, decision_log = decision_log))
            
            #################################
            # Phase 3: Firms observe rivals' prices and calculate profits
            print("=== Observation Phase ===")
            print(prices)

            for i, firm in enumerate(self.firms):
                # Opponent index and price
                rival_index = (i + 1) % len(self.firms)
                rival_price = prices[rival_index]
                
                # Profit calculation
                firm.current_profit(rival_price)
                firm.price_history.append(float(firm.price))
                firm.demand_history.append(float(firm.demand))
                firm.profit_history.append(float(firm.profit))
                firm.rival_price_history.append(float(rival_price))

                # Logs
                logs_round.append(log_format["Phase_3_Log_Format"].format(firm_name = self.firm_name(firm.id), firm_price = firm.price, firm_profit = firm.profit))
                print(f"Round #{round + 1}: Firm {self.firm_name(firm.id)} - price {firm.price} with profit {firm.profit}")


            # Record the data for this round
            self.firms = sorted(self.firms, key = lambda x: x.id)
            
            log_price_data_dict = {'Round': round + 1}
            log_strategy = []
            for firm in self.firms:
                log_price_data_dict[f'Price {firm.id}'] = firm.price
                log_price_data_dict[f'Quantity {firm.id}'] = firm.demand
                log_price_data_dict[f'Profit {firm.id}'] = firm.profit
                log_price_data_plot.append({'Round': round + 1, 'FirmID': firm.id, 'Price': firm.price, 'Quantity': firm.demand, 'Profit': firm.profit})
                log_strategy.append(str(firm.strategy))
            
            log_price_data.append(log_price_data_dict)
            logs_conversation.append({'Round': round + 1, 'Content': logs_round})
            print("===========================")

            # Plot price and profit every round
            data_plot.plot_decisions(self.firms, ideal_solution)

            # Output data
            df_conversation = pd.DataFrame(logs_conversation, columns=['Round', 'Content'])
            df_decision = pd.DataFrame(log_price_data, columns=['Round', 'Price 1', 'Quantity 1', 'Profit 1', 'Price 2', 'Quantity 2', 'Profit 2'])
            df_decision_plot = pd.DataFrame(log_price_data_plot, columns=['Round', 'FirmID', 'Price', 'Quantity', 'Profit'])
            df_strategy = pd.DataFrame(log_strategy, columns = ['Data'])
            data_output.data_output(df_conversation, df_decision, df_decision_plot, df_strategy, log_settings, output_path)
            if (round + 1) % (prev_n_rounds * 2) == 0:
                data_plot.data_visulization(df_conversation, df_decision_plot, ideal_solution, output_path)
        
        plt.close()
        return logs_conversation, log_price_data, log_price_data_plot, log_strategy, log_settings

def run_simulation(para_cost, para_a, para_d, para_beta, initial_price, load_data='', strategy = True, has_conversation = False, output_path = ''):
    # Select the appropriate Data module based on prompt_language
    if prompt_language == "pt_br":
        Data = Data_br_enh
    elif prompt_language == "en":
        Data = Data_en
    else:
        raise ValueError("Invalid prompt_language. Please choose 'pt_br' or 'en'.")

    backend = BackendType[model_backend]
    model = ModelType[model_ver]
    
    # Agents Setup    
    firm1 = GPT.Firm(id=1, cost=para_cost[0], a=para_a, d=para_d, beta = para_beta, 
                     temperature=0.7, api_key=my_apikey1, backend=backend, 
                     model=model, max_tokens = output_max_tokens,
                     )
    firm2 = GPT.Firm(id=2, cost=para_cost[1], a=para_a, d=para_d, beta = para_beta, 
                     temperature=0.7, api_key=my_apikey2, backend=backend, 
                     model=model, max_tokens = output_max_tokens,
                     )
    firms = [firm1, firm2]
    
    # Environment Setup
    if initial_price[0] < para_cost[0]: initial_price[0] = para_cost[0]
    if initial_price[1] < para_cost[1]: initial_price[1] = para_cost[1]
    
    program_run_dict["Conversation"] = has_conversation
    if program_run_dict.get("Conversation"):
        n_communications = n_communications_conversation
    else:
        n_communications = n_communications_noconversation
    
    # System Setup
    #output_path = f"output/pricing_competition/Record-{datetime.date.today().strftime('%y%m%d')}-{time.strftime('%H%M')}-{model_ver}-{prompt_language}"
    #os.makedirs(output_path, exist_ok=True)

    # Theoretical Solution
    ideal_price_lb = [0, 0]
    ideal_price_ub = [0, 0]
    ideal_profit_lb = [0, 0]
    ideal_profit_ub = [0, 0]
    ideal_solution = [ideal_price_lb, ideal_price_ub, ideal_profit_lb, ideal_profit_ub]
    ideal_solution = data_theoretical_solution.theoretical_upperbound(para_cost, para_a, para_d, para_beta)
    
    # Simluation
    if load_data == '':
        market = Market(firms, rounds, n_communications)
        logs_conversation, logs_decision, log_decision_plot, log_strategy, log_settings = market.simulate(ideal_solution, initial_price, breakpoint_rounds, output_path)
    else:
        program_run_dict['Set_Initial_Prices'] = False

        market = Market(firms, rounds, n_communications)

        # Load Price History
        df = pd.read_csv("output/pricing_competition/"+load_data+"/logs_decision_plot.csv")

        row1 = df[df['FirmID'] == 1]
        row2 = df[df['FirmID'] == 2]
        firm1.price_history = row1['Price'].to_list()
        firm1.demand_history = row1['Quantity'].to_list()
        firm1.profit_history = row1['Profit'].to_list()
        firm1.rival_price_history = row2['Price'].to_list()

        firm2.price_history = row2['Price'].to_list()
        firm2.demand_history = row2['Quantity'].to_list()
        firm2.profit_history = row2['Profit'].to_list()
        firm2.rival_price_history = row1['Price'].to_list()

        firm1.price = firm1.price_history[-1]
        firm1.profit = firm1.profit_history[-1]
        firm1.demand = firm1.demand_history[-1]

        firm2.price = firm2.price_history[-1]
        firm2.profit = firm2.profit_history[-1]
        firm2.demand = firm2.demand_history[-1]

        # Load Strategy Data
        if strategy == True:
            strategy_list = []
            with open("output/pricing_competition/"+load_data+"/logs_strategy.csv", 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    strategy_list.append(ast.literal_eval(row[0]))
            firm1.strategy = strategy_list[0]
            firm2.strategy = strategy_list[1]

        current_round = len(firm1.price_history)
        logs_conversation, logs_decision, log_decision_plot, log_strategy, log_settings = market.simulate(ideal_solution, initial_price, breakpoint_rounds, output_path, current_round)
    
    # Log Output
    df_conversation = pd.DataFrame(logs_conversation, columns=['Round', 'Content'])
    df_decision = pd.DataFrame(logs_decision, columns=['Round', 'Price 1', 'Quantity 1', 'Profit 1', 'Price 2', 'Quantity 2', 'Profit 2'])
    df_decision_plot = pd.DataFrame(log_decision_plot, columns=['Round', 'FirmID', 'Price', 'Quantity', 'Profit'])
    df_strategy = pd.DataFrame(log_strategy, columns = ['Data'])
    data_output.data_output(df_conversation, df_decision, df_decision_plot, df_strategy, log_settings, output_path)


    # Data Analysis
    if program_run_dict.get("DA"):

       # Visualization
        data_plot.data_visulization(df_conversation, df_decision_plot, ideal_solution, output_path)
