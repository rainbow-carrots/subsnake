class Keys():
    def __init__(self):
        self.key_table = {
            65: 0,  #a
            87: 1,  #w
            83: 2,  #s
            69: 3,  #e
            68: 4,  #d
            70: 5,  #f
            84: 6,  #t
            71: 7,  #g
            89: 8,  #y
            72: 9,  #h
            85: 10, #u
            74: 11, #j
            75: 12, #k
            79: 13, #o
            76: 14, #l
            80: 15, #p
            59: 16, #;
            39: 17, #'
            43: 18, #+
            45: 19  #-
        }
    
    def key_offset(self, key):
        return self.key_table.get(key)
