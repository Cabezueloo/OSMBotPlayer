class Player:
    def __init__(self,name,pos,age,club,att,deff,ovr,priceToBuy,realPrice):
        self.name = name
        self.pos = pos
        self.age = age
        self.club = club
        self.att = att
        self.deff = deff
        self.ovr = ovr
        self.priceToBuy = priceToBuy
        self.realPrice = realPrice
        self.inflated = (self.priceToBuy - self.realPrice) /self.realPrice * 100
        self.avrMedia = (att+deff+ovr)//3
    

    def __eq__(self, other):
        return self.avrMedia == other.avrMedia and self.inflated == other.inflated

    def __lt__(self, other):
        if self.inflated == other.inflated:
            return self.avrMedia > other.avrMedia  # Ordena `avrMedia` de mayor a menor
        return self.inflated < other.inflated       # Ordena `inflated` de menor a mayor


        
    def __str__(self):
        return (f"Nombre: {self.name}, Posición: {self.pos}, Edad: {self.age}, Club: {self.club}, "
                f"Valoración de Ataque: {self.att}, Valoración de Defensa: {self.deff}, "
                f"Valoración General: {self.ovr}, Precio de Compra: {self.priceToBuy}, "
                f"Precio Real: {self.realPrice}, Inflación: {self.inflated:.2f}%")