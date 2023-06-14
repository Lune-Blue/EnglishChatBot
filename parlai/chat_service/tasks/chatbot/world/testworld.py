#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
# py parlai/chat_service/tasks/overworld_demo/run.py --debug --verbose

from parlai.core.worlds import World
from parlai.chat_service.services.messenger.worlds import OnboardWorld
from parlai.core.agents import create_agent_from_shared
from parlai.convai.persona_extraction import persona_extract
from parlai.convai.topic_extraction import topic_extract

# ---------- Chatbot demo ---------- #
class MessengerBotChatOnboardWorld(OnboardWorld):
    """
    Example messenger onboarding world for Chatbot Model.
    """

    @staticmethod
    def generate_world(opt, agents):
        return MessengerBotChatOnboardWorld(opt=opt, agent=agents[0])

    def parley(self):
        self.episodeDone = True


class MessengerBotChatTaskWorld(World):
    """
    Example one person world that talks to a provided agent (bot).
    """

    MAX_AGENTS = 1
    MODEL_KEY_1 = 'dodecadialogue1'
    MODEL_KEY_2 = 'dodecadialogue2'

    def __init__(self, opt, agent, bot1, bot2):
        self.agent = agent
        self.episodeDone = False
        self.model1 = bot1
        self.model2 = bot2
        self.first_time = True

    @staticmethod
    def generate_world(opt, agents):
        if opt['models'] is None:
            raise RuntimeError("Model must be specified")
        return MessengerBotChatTaskWorld(
            opt,
            agents[0],
            create_agent_from_shared(
                opt['shared_bot_params'][MessengerBotChatTaskWorld.MODEL_KEY_1]
            ),
            create_agent_from_shared(
                opt['shared_bot_params'][MessengerBotChatTaskWorld.MODEL_KEY_2]
            ),            
        )

    @staticmethod
    def assign_roles(agents):
        agents[0].disp_id = 'ChatbotAgent'

    def parley(self):
        if self.first_time:
            get_topic = topic_extract()
            get_persona = persona_extract()
            print(get_topic[0])
            for i in range(0,4):
                self.model1.observe({'id':'context', 'text':"your persona:"+get_persona[i], 'episode_done':False})
                print("your persona:" + get_persona[i])
            self.model1.observe({'id':'context', 'text':"topic:"+get_topic[0], 'episode_done':False})
            self.model2.observe({'id':'context', 'text':"topic:"+get_topic[0], 'episode_done':False})
            print("topic:" + get_topic[0])      
            self.agent.observe(
                {
                    'id': 'World',
                    'text': 'Welcome to Convai Lab Chatbot demo.'
                    'You are now paired with a bot - feel free to send a message.'
                    'Type [DONE] to finish the chat, or [RESET] to reset the dialogue history.' + "|"
                    "Topic is '" + get_topic[0]+ "'|" +
                    'Bot persona is ' + " 1." + get_persona[0] + " 2." + get_persona[1] + " 3." + get_persona[2] + " 4." + get_persona[3]
                    ,
                }
            )
            self.first_time = False
        a = self.agent.act()
        if a is not None:
            if '[DONE]' in a['text']:
                self.episodeDone = True
            elif '[RESET]' in a['text']:
                self.model1.reset()
                self.model2.reset()
                self.agent.observe({"text": "[History Cleared]", "episode_done": False})
            else:
                print("===act====")
                print(a)
                print("~~~~~~~~~~~")
                self.model1.observe(a)
                self.model2.observe(a)
                response_1 = self.model1.act()
                save_response = response_1['text']
                self.model2.observe(response_1)
                response_2 = self.model2.act()
                print("===response_1====")
                print(response_1)
                print(response_1['text'])
                print("===response_2====")
                print(response_2['text'])
                del(response_1['text'])
                response_1['text'] = save_response + "|" + response_2['text']
                print(response_1)
                self.agent.observe(response_1)

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        self.agent.shutdown()


# ---------- Overworld -------- #
class MessengerOverworld(World):
    """
    World to handle moving agents to their proper places.
    """

    def __init__(self, opt, agent):
        self.agent = agent
        self.opt = opt
        self.first_time = True
        self.episodeDone = False

    @staticmethod
    def generate_world(opt, agents):
        return MessengerOverworld(opt, agents[0])

    @staticmethod
    def assign_roles(agents):
        for a in agents:
            a.disp_id = 'Agent'

    def episode_done(self):
        return self.episodeDone

    def parley(self):
        if self.first_time:
            self.agent.observe(
                {
                    'id': 'Overworld',
                    'text': 'Welcome to the Convai Lab messenger '
                    'chatbot demo. Please type "begin" to start, or "exit" to exit',
                    'quick_replies': ['begin', 'exit'],
                }
            )
            self.first_time = False
        a = self.agent.act()
        if a is not None and a['text'].lower() == 'exit':
            self.episode_done = True
            return 'EXIT'
        if a is not None and a['text'].lower() == 'begin':
            self.episodeDone = True
            return 'default'
        elif a is not None:
            self.agent.observe(
                {
                    'id': 'Overworld',
                    'text': 'Invalid option. Please type "begin".',
                    'quick_replies': ['begin'],
                }
            )
