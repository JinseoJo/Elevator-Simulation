class F:
    def __init__(self):
        self.item = 0
G = F()
l = [1, 2, 3, G, 'h']
l.remove(G)
print(l)
