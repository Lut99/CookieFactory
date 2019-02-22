from Tools import Date
import time

d = Date(22, 22, 2, 2019)

for i in range(50):
    d.tick(24)
    print(d)
    time.sleep(.1)