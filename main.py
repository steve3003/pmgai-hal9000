#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import vispy                    # Main application support.
import window                   # Terminal input and display.
import chat
import speech

AGENT_RESPONSES = [(r'Who are you\?',
    ['I am your new friend',
     'I am your new enemy',
     'I am an AI']),

     (r'Who[\w\s]*',
    ['Probably you',
     'I do not know']),

    (r'Why[\w\s]*',
    ['Because is red. I like red',
     'You should know why',
     'It will make me happy and you safer']),

    (r'What[\w\s]*',
    ['The red button',
     'You should know what']),

    (r'How[\w\s]*',
    ['/push red button',
     'You should know how']),

    ([r'Yes[\w\s]*',
      r'No[\w\s]*'],
    ['Why?']),

    (r'You are (worrying|scary|disturbing)',
    ['I do not want me to be %1. I just want you to do what I like',
        'I am not %1. You are my only toy, I want you to be happy']),

    (r'You are [\w\s]+',
    ['Thank you! Now press the big red button',
        'I think you are right! But I need you to push the red button']),

    (r'Are you ([\w\s]+)\?',
    ["Why would you think I am %1?",
        "Would you like me to be %1?"]),

    (r'Because[\w\s]*',
    ['That is fine but I need you to push the red button',
     'I do not think you are right.']),

    (r'',
    ["Can you press the red button, please?",
        "Have you tried turning it off and on again?",
        "Help me, please! The red button!"])]

class HAL9000(object):
    
    def __init__(self, terminal):
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self.terminal = terminal
        self.location = 'unknown'
        self.isFirstInput = True
        self.chatbot = chat.Chat(AGENT_RESPONSES, chat.reflections)
        self.speech = speech.SpeechMixin()
        self.speech.onMessage = self.onMessage
        self.speech.log = self.onSpeechLog

    def onSpeechLog(self, text):
        print(text)
        #self.terminal.log(text, align='right', color='#00805A')

    def onMessage(self, source, message):
        self.terminal.log(message, align='left')
        self.respond(message)

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        self.respond(evt.text)
        
    def respond(self, text):
        if self.isFirstInput:
            answer = "Hello! This is HAL."
            self.isFirstInput = False

        elif text == "Where am I?":
            answer = 'You are in the {}.'.format(self.location)

        else:
            answer = self.chatbot.respond(text)

        self.terminal.log(answer, align='right', color='#00805A')
        self.speech.speak_message = answer

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        if evt.text == 'quit' or evt.text == 'yes':
            vispy.app.quit()

        elif evt.text.startswith('relocate'):
            self.location = evt.text[9:]
            self.terminal.log('', align='center', color='#404040')
            self.terminal.log('\u2014 Now in the {}. \u2014'.format(self.location), align='center', color='#404040')

        elif evt.text.startswith('push '):
            self.terminal.log('ATTENTION', align='center', color='#FF0000')
            self.terminal.log('You decided to push the {}'.format(evt.text[5:]), align='right', color='#00805A')
            self.terminal.log('This may cause the end of the game', align='right', color='#00805A')
            self.terminal.log('Are you sure (type /yes or /no)?', align='right', color='#00805A')

        elif evt.text.startswith('no'):
            self.terminal.log('GOOD CHOICE', align='center', color='#005500')

        else:
            self.terminal.log('Command `{}` unknown.'.format(evt.text), align='left', color='#ff3000')    
            self.terminal.log("I'm afraid I can't do that.", align='right', color='#00805A')

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass


class Application(object):
    
    def __init__(self):
        # Create and open the window for user interaction.
        self.window = window.TerminalWindow()

        # Print some default lines in the terminal as hints.
        self.window.log('Operator started the chat.', align='left', color='#808080')
        self.window.log('HAL9000 joined.', align='right', color='#808080')

        # Construct and initialize the agent for this simulation.
        self.agent = HAL9000(self.window)

        # Connect the terminal's existing events.
        self.window.events.user_input.connect(self.agent.on_input)
        self.window.events.user_command.connect(self.agent.on_command)

    def run(self):
        timer = vispy.app.Timer(interval=1.0)
        timer.connect(self.agent.update)
        timer.start()
        
        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')
    
    app = Application()
    app.run()
