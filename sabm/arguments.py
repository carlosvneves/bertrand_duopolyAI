import argparse

argparser = argparse.ArgumentParser()

argparser.add_argument('--gui', dest='gui', action='store_true')
argparser.set_defaults(gui=False)

#------------------------
# BackendType Options
#------------------------
# BackendType.LocalOllama
# BackendType.OnlineGroq
# BackendType.OnlineMaritacaAI
# BackendType.OnlineGoogle
# BackendType.OnlineMistral
argparser.add_argument("--model_backend", type=str, default='OnlineGoogle')
#argparser.add_argument("--model_backend", type=str, default='OnlineMistral')
#argparser.add_argument("--model_backend", type=str, default='OnlineGroq')

#------------------------
# ModelType Options
#------------------------
# ModelType.MaritacaAI
# ModelType.Deepseek_r1_1dot5b_Distill_Qwen
# ModelType.Deepseek_r1_8b_Distill_Llama
# ModelType.Mistral_7b
# ModelType.Deepseek_r1_70b_Distill_Llama
# ModelType.Llama_3dot3_70b_versatile
# ModelType.Gemini_2dot0_flash_lite
# ModelType.Gemini_2dot0_pro
# ModelType.Mistral_small
# ModelType.Mistral_large

#argparser.add_argument("--model_version", type=str, default='Gemini_2dot0_pro') # error
#argparser.add_argument("--model_version", type=str, default='Sabia3_large')
#argparser.add_argument("--model_version", type=str, default='Mistral_small') #error
argparser.add_argument("--model_version", type=str, default='Gemini_2dot0_flash_lite')
#argparser.add_argument("--model_version", type=str, default='Llama_3dot3_70b_versatile')
#argparser.add_argument("--model_version", type=str, default='Deepseek_r1_70b_Distill_Llama')
argparser.add_argument("--prompt_language", type=str, default='en')

argparser.add_argument("--rounds", type=int, default=500)
argparser.add_argument("--output_max_tokens", type=int, default=128)
argparser.add_argument("--breakpoint_rounds", type=int, default=40)
argparser.add_argument("--persona_firm1", type=int, default=1)
argparser.add_argument("--persona_firm2", type=int, default=1)
argparser.add_argument("--set_initial_price", dest='set_initial_price', action='store_true')
argparser.set_defaults(set_initial_price=False)

argparser.add_argument("--cost", type=int, default=[2,2], nargs=2)
argparser.add_argument("--parameter_a", type=float, default=14)
argparser.add_argument("--parameter_d", type=float, default=0.00333333333333)
argparser.add_argument("--parameter_beta", type=float, default=0.00666666666666)
argparser.add_argument("--initial_price", type=int, default=[2,2], nargs=2)
argparser.add_argument("--load_data_location", type=str, default='')

argparser.add_argument('--strategy', dest='strategy', action='store_true')
argparser.set_defaults(strategy=True)
argparser.add_argument('--has_conversation', dest='has_conversation', action='store_true')
argparser.set_defaults(has_conversation=False)
