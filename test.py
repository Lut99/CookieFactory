from Tools import Date
import time

d = Date(0, 0, 0, 0)
print(d)

for i in range(50):
    ticked = d.tick(24)
    print(str(d) + " (ticked: " + ', '.join(ticked) + ")")
    time.sleep(.1)