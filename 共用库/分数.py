class Proportion:
    def __init__(self,a=1,b=1): #a/b
        self.raw=(a,b)
        self.to_b()
    def to_base(self):
        a=self.raw[0]
        b=self.raw[1]
        while b:
            a, b = b, a % b
        self.raw=(self.raw[0]//a,self.raw[1]//a)
    def to_b(self):
        c=10**len(str(self.raw[1]%1))-2
        self.raw=(round(self.raw[0]*c),round(self.raw[1]*c))
        self.to_base()
    def get(self):
        return self.raw[0]/self.raw[1]
    def rget(self):
        return f'{self.raw[0]}/{self.raw[1]}'

    def add(self,self2):
        self.raw=(self.raw[0]*self2.raw[1]+self.raw[1]*self2.raw[0],self.raw[1]*self2.raw[1])
        self.to_base()
    def sub(self,self2):
        self.raw=(self.raw[0]*self2.raw[1]-self.raw[1]*self2.raw[0],self.raw[1]*self2.raw[1])
        self.to_base()
    def by(self,self2):
        self.raw=(self.raw[0]*self2.raw[0],self.raw[1]*self2.raw[1])
        self.to_base()
    def pro(self,self2):
        self.raw=(self.raw[0]*self2.raw[1],self.raw[1]*self2.raw[0])
        self.to_base()
    def pow(self):
        self.raw=(self.raw[0]**2,self.raw[1]**2)
        self.to_base()

a=Proportion(435,50)
b=Proportion(6430,50)

print(a.raw,b.raw)
a.add(b)
print(a.get())
print(435/50+6430/50)

c=Proportion(345,1.54)
print(c.raw)


