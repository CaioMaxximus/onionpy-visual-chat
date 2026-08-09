from .basic_chat_view import BasicChatView
import random
class ClientGUI(BasicChatView):

    """
        The class represents the client side chat interface.

        It add to the base class behaviour by establishing his own
        schedule of actions to perform in the initialization process
        and some visual changes
    """

    def __init__(self ,master, name , controller, host , port):

        super().__init__(master , controller)
        self.host = host
        self.port = port
        self.controller =  controller
        self.master = master
        self.title("Client Onion conneciton")
        self.name = name

        
        def _on_start(self): 
            def started_callback():
                self.start_routines()
                self.running = True
                self.controller.start_client(name ,lambda server_data : self.build_interface(server_data))
            self.controller.run(self.host,self.port , self.master , started_callback)
        _on_start(self)
    


    def build_interface(self,server_data):
        super().build_interface()
        host_info = f"{server_data['name']} \n Connected to : \n {self.host}:{self.port}"
        self.title(f"Active chat : {self.host[0:10]}...")
        self.top_info.configure(text=host_info)
        self.send_automated_msg()


    ##  Function used to test canvas rendering 
    def send_automated_msg(self):
        text = """This enables interactive audiences while futurize calibrateing real-time blockchain-enabled out-of-the-box footprints.
                    Reposition immersive impressions systems across service-oriented out-of-the-box results-oriented data-lakes skunkworks.
                    By leverageing virtual accelerators, organizations can aggregate innovative compelling methodologies. By decomposeing streamlined dashboards environments, organizations can productize Speed conversions. Catalyze moonshot business-units across compelling decoupled synergistic dashboards heatmaps. A B2C compelling optimized assessments use-cases designed to synthesize modular ultra-low-latency distributed imperatives metrics.
                   """

        nums = [ random.randint(0, len(text) - 1), random.randint(0, len(text) - 1)]
        time_interval = random.randint(850, 1600)
        s = min(nums)
        e = max(nums)
        self.add_my_message(text[s:e])
        self.master.after(time_interval,self.send_automated_msg)