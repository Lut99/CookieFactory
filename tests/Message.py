import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Interface

# Run the verifier
Interface.verify_mapping()

# Create a test message
test = Interface.Message(Interface.CONNECTION_REQUEST)
test.password = "test"

# Convert to bytes
bts = test.pack()
print(bts)

# Try to convert it back into a password again
test_back = Interface.Message(Interface.CONNECTION_REQUEST, bts)
print(test_back.password)
