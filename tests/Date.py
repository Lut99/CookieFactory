from Tools import Date
import time
import random

d = Date(0, 0, 0, 0)

ticked = []
start = time.time()
for i in range(1000000):
    # Depochify
    hour, day, month, year = Date.depochify(d.epoch)
    epoch = Date.epochify(hour, day, month, year)

    equal = d.epoch == epoch
    if not equal:
        print(f"Mismatch found: {d.getdate()}")
        break

    if time.time() - start > 1:
        print(f"Current date: {d.getdate()} / Target date: {Date(epoch=1000000 * 24)}")
        start = time.time()

    # Update time
    ticked = d.tick(24)

print("Done.")