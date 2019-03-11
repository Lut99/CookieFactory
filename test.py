from Tools import Date
import time

d = Date(0, 0, 0, 0)

ticked = []
for i in range(250):
    hour, day, month, year = Date.depochify(d.epoch)
    epoch = Date.epochify(hour, day, month, year)
    print(str(d) + " (ticked: [" + ', '.join(ticked) + "], epoch - epochify(depochify): " + str(epoch - d.epoch) + ")")
    ticked = d.tick(24)
    time.sleep(.1)