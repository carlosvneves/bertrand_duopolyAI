import datetime
import time

from sabm.arguments import argparser
import sabm.pricing_competition as competition
from dotenv import load_dotenv
import os



load_dotenv()

try:
    # api_key = os.environ["OPENAI_API_KEY"]
    api_key1 = os.environ["MARITACA_API_KEY_AG1"]
    api_key2 = os.environ["MARITACA_API_KEY_AG2"]
except:
    api_key = open("apikey.token").readline().strip()


def main(args):
    competition.my_apikey1 = api_key1
    competition.my_apikey2 = api_key2
    competition.model_backend = args.model_backend
    competition.model_ver = args.model_version
    competition.prompt_language = args.prompt_language
    competition.rounds = args.rounds
    competition.output_max_tokens = args.output_max_tokens
    competition.breakpoint_rounds = args.breakpoint_rounds
    competition.firm_persona_1 = args.persona_firm1
    competition.firm_persona_2 = args.persona_firm2
    competition.program_run_dict["Set_Initial_Prices"] = args.set_initial_price

    model_ver = competition.model_ver
    prompt_language = competition.prompt_language

    # System Setup
    output_path = f"output/pricing_competition/Record-{datetime.date.today().strftime('%y%m%d')}-{time.strftime('%H%M')}-{model_ver}-{prompt_language}"
    os.makedirs(output_path, exist_ok=True)

    competition.run_simulation(
        args.cost,
        args.parameter_a,
        args.parameter_d,
        args.parameter_beta,
        args.initial_price,
        args.load_data_location,
        args.strategy,
        args.has_conversation,
        output_path,
    )



if __name__ == "__main__":
    args = argparser.parse_args()
    main(args)
