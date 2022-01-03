from testsignaller import Signaller

class Camera():
    def __init__(self, signaller) -> None:
        self.signaller = signaller
        
    def test(self):
        self.signaller.message("Message")