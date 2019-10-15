# Changelog:
- v0.1.0 (alpha):
  - Begun development
- v0.2.0 (alpha):
  - Begun work of Logistics System
  - Finished Worker System
- v0.3.0 (alpha):
  - Deleted all Logistic System due to the fact that modules had too little
    control and only one storage, making that certain logistic flows were
    impossible. Instead completely redesigning to allow modules more control
- v0.4.0 (alpha):
  - Begun debugging the logistics system
  - After a lot of fucking about with the logistics system, finally got it to
    work
- v0.5.0 (alpha):
  - Begun adding recipes
  - Moved most classes to Tools.py
  - Changed CSV loading to have it's own function in Tools.py
- v0.6.0 (alpha):
  - Added production chains
  - Finished recipes
- v0.7.0 (alpha):
  - Added interface
  - Reworked the archive to note interface-relevant data
  - Added the ability to log on the interface console
  - Changed factory running forgo threading and instead
    work one-call-at-a-time related
- v0.8.0 (alpha):
  - Added plots to the interface
  - Changed Date() to work with correct days per month (e.g., February has 28)
  - Changed Date() to work with epochs since 00:00:00 00/00/0000 to support
    correct days format
- v0.9.0 (alpha):
  - Removed the existing interface
  - Instead, uses another application in Swift that communicates to the
    simulation with TCP sockets
- v0.9.1 (alpha):
  - Reorganized files to a more structured and logical approach

# Roadmap
Sidenote: everything in *cursive* is TODO
- v1.0.0: The Release
  - Add Factory infrastructure (programatically, then)
  - Add the basic Factory modules:
    - Office
    - Human Resources
    - Logistics
    - Depot
    - Archive
  - Add recipes & production chains
  - Add UI
  - *Finish the depochify() function of Date class*
  - *Interface:*
    - *Add console*
    - *Add general information*
    - *Add factory-specific information*
    - *Add settings*
    - *Add plots*
    - *Add yearly news-paper ish event logs*
  - *Add Storage, Mixer and Oven*
  - *Add automizing production chains*
  - *Let the factory make income*

- vX.0.0: The Visual Update
  - *Interface:*
    - *Add LAYOUT OF THE FACTORY???*

# The Products

# The Factory Process

The factory is simply a collection of modules. There are some administrative
modules, required for the logistics and administration of a factory. But most
modules are actually product-related: an oven, a mixing station, etc. Each
modules requires workers, and might have specific requirements (e.g. a certain
education, a minimum / maximum age, etc.). A factory can, if required and
desired, purchase new modules to increase operation.

Workers are small entities. They require to be paid "in fairness": if not paid
enough, they will refuse to work or even resign. The workers are assigned to a
module for certain hours of certain days, and do their thing there. Certain
factors, such as extra safety, having lunch breaks or not having to work in
weekends can decrease the minimum amount of salary a worker requires before he
goes on strike.

These modules together create a final product, probably cookies, which can be
sold on The Market. Requirements for these products (dough, milk, or stuff like
iron) can be purchased on The Market. In future editions of this program,
multiple factories might sustain each other. But for now, The Market is
presumed to have infinite stock of stuff, and infinite demand for stuff.

## Modules
The factory has a few bare-essential modules, needed for normal factory
process, regardless of the actual product(s) the factory makes:
- Office:  
  The office is the main part of the factory. It manages all money flows, and,
  more importantly, all optimisations done in the factory (buying new modules,
  purchasing new recipes, ordering new researches, etc.)
- Human Resources:  
  Human resources is the second main part of the factory. This module is in
  charge of hiring, firing and paying all workers in the factory.
- Logistics:  
  Logistics is the thirdmost main part of the factory. This module is in
  control of the goods flow from the market to the market again (but not the
  actual buying or selling).
- Depot:  
  The Depot is tied with the Logistics module, regarding importance in the
  factory. In fact, it can be seen as an extension to the Logistics module. The
  Depot is the link between the Factory and the outside world regarding
  resources. The Factory can sell or buy resources through this way.
- Archive:  
  Module that has a somewhat more abstract influence on the Factory process.
  Keeps track of all stats across the factory, to allow for decision-making and,
  maybe even more important, visualising the Factory's day-to-day process.

Then there are some modules that aren't required exactly, but aren't related
to a specific product either:



Finally, we have product specific modules. These often come in a Chain, linking
the modules together and allowing easier management of one product:


## Systems
- Worker System:  
  The worker system is one of the three backbones of a factory. Without workers, 
  the factory would not be able to run at all. The worker system is managed 
  (alsmost) completely by Human Resources. The basic idea is that every module
  needs certain types of workers, defined by the Positions, that need to be
  filled in with a willing slave. This slave is supposed to be human, so it has
  to rest occasionally, or else he or she will run out of energy and simply
  stop working. It also requires pay, which is order by Human Resources but
  eventually paid by the Office.

  That's why, every hour, Human Resources checks for each worker whether their
  shift (defined by their Position) is ended, and, if so, sends them home. At
  the same time, if the shift of a worker starts, the Human Resources checks
  him in.

  The second job of Human Resources is to fire workers that have no longer a
  place in the factory. There are several reasons why a worker would be fired:
  - He's too old (older than 67 yrs)
  - He isn't working hard enough (more about that in a bit)
  - The position the worker was working is no longer available
  - The worker isn't paid enough (this is actually a resignation, but a handled
     as if the worker was fired because there's no damn difference).
  
  Accompanied with this is checking whether a worker works hard enough. Human
  Resources does this by checking how many days the worker has worked in total,
  and comparing that to how many days of those the worker stopped working
  (energy depleted). If the worker spends more than half his days slumbering, he
  or she is fired.

  To replace the fired workers, or to get workers to begin with, Human Resources
  also hires new people. This is where the human resources team comes in: every
  month, one worker can hire one new worker for the factory (the only exception
  to this are workers for Human Resources. They magically hire themselves).
  Accompanied with a position is the minimum amount of education a worker should
  have to be able to do a job, which is the measure by which they determine if
  you can be hired or not.

- Logistics System:  
  The logistic system is another one of the Factory backbones. It handles all
  resource transferring between modules, which means that without, the factory
  wouldn't have any resources to work with. The logistic system relies on
  Storages, and by extension, Storage Rules. Each module can assign itself a
  storage of specified size. Then, it can specify the rules of that storage.
  Each rule can talk about one item (or all of them, using the '*'), and can
  control the following:
  - The desired amount of that item in the storage
  - The logic flow (In, Out, or both)
  - The target modules, aka, modules that can receive from / deliver to this
    storage with this item
  - The 'anti-target' modules: modules that CANNOT receive from / deliver to
    this storage with this item.  

  Once those rules are specified, the Logistics module will then try to bring
  these around according to the rules. It hauls items every hour, and when it
  does, it begins by collecting all desired items (storage's items of which the
  rules are In or InOut and of which there are less stored than desired) and
  offered items (storage's items of which the rules are Out or InOut and of
  which there are more stored than desired). Then, it delivers these, by driving
  a forktruck from one storage to the other, hauling a specific amount of items
  per time. They can only haul one type of item for one rule, so beware. Each
  forktruck can only be driven by one worker, and one worker can only drive one
  truck. In the case that there are offers and / or requests left that cannot be
  satisfied by the other rules (and there are still workers left), the system
  will satisfy these rules with the depot if their target and antitarget modules
  property holds for the depot (by default, it doesn't).

- The Market:  
  The Market is an abstract idea, representing the rest of the world the
  factory can interact with. At first, the market is static: there are endless
  resources and the prices don't change depending on how many bought or sold.
  However, in later versions, the market is a dynamic model: there is a pool of
  resources, and factories get less for items if they are sold in huge amounts.

# The Cookie Factory Network Protocol (CFNP)
In order for an Interface to connect with the simulation, a network protocol
was devised. This is a single protocol that handles terminal input / output,
archive information and world information. It works over TCP, so we don't
have to be concerned by stream order or completeness.

As an additional security layer, the CFNP requires the user to enter a password
right after connection is made in order to continue. Upon failure, the user is
rejected.

## The Header
The most important part of this protocol is the header. It exists out of X
bytes in total, which looks as follows.
The first byte marks the operator code, which in turn determines what type
of information is being send. So far, these opcodes have a meaning:
  - 0x00: Connection Request            (PASSWORD)
  - 0x01: Connection Accept             (PASSWORD)
  - 0x02: Terminal Public Output Send   (TERMINAL)
  - 0x03: Terminal Private Output Send  (TERMINAL)
  - 0x04: Terminal Input Send           (TERMINAL)
  - 0x05: Terminal Sync Request         (TERMINAL)
  - 0x06: Terminal Sync Response        (TERMINAL)
  - 0x07: Terminal Message              (TERMINAL)
Each opcode belongs to a subprotocol, which is indicated in the brackets at
the end. Please see below for more information about these subprotocols.

An operator code of -1 means that the connection has timed out

Following the opcode will be a 32-bit number, which specifies the total message
size after the opcode and the length. This way, the receiver knows how many
bytes to expect.

## The Fourth Handshake (PASSWORD)
Aside from the way that incoming messages are read, the CFNP also provides
additional security by only allowing access to those with a password. There
are two messages for those, the request and the accept. The user is simply
disconnected without any message if the password was incorrect.

### Connection Request
This is the message that the user sends to the server upon initiating contact.
Aside from the default headers, this message contains no other than the password.

### Connection Accept
If the user has entered a correct password, they will be greeted by this message.
It is nothing more than the default header but then with this opcode.

## Terminal Output / Input (TERMINAL)
An important part of the CFNP is the syncing of general output information
across the Interfaces. The basic idea is that each Interface holds an internal
terminal log that is updated by the Terminal Public Output Send. Should this
log get out of sync with the server, the Interface is supposed to send a sync
request back to the server in which it downloads the entire terminal again.
Additionally, the Interface also has to maintain a private terminal log with
messages only for that particular Interface. This needn't be synced, and is
only for replies from commands the user sends to the server.

A list of the error status codes for the messages:
  - 0x00: Information
  - 0x01: Warning
  - 0x02: Fatal Error
  - 0x03: Command Information
  - 0x04: Command Parse Error
  - 0x05: Command Run Error

### Terminal Public Output Send
During a Terminal Public Output Send, the server sends each interface a new
message from the simulation. The header that is matched to this opcode has the
following structure. First, there will be a checksum of 8 bytes long, that is
used to check if the receiver is still in sync with the sender. Then comes the
message, which is in the format as specified by Terminal Message.

This type of message can be send at any time, and not just as a response to a
Terminal Input Send.

### Terminal Private Output Send
During a Terminal Private Output Send, the server sends the interface a new
message - but only this interface. This is normally the result of a command,
and therefore has a much simpeler structure. No checksum is needed, as this
type of message does not need to be synced with the server. That's why there's
the message metadata immediately, which consists of a message error status
(1 byte), a real-life timestamp (8 bytes). The remained of the message is the
actual terminal message, in string format.

This type of message is usually only in response to a Terminal Input Send.

### Terminal Input Send
When the user types a command in the interface, a Terminal Input Send is send
to the server. This has a fairly simple structure: First is a real-life
timestamp of 8 bytes. Immediately afterwards is the message that the user send,
in string, which the server will parse and then interpret.

Based on what command and the success status of it, the terminal will then
receive either a Terminal Private Output Send or a Terminal Public Output Send.

### Terminal Sync Request
The Terminal Sync Request is a very simple command. It simply exists out of the
normal header, and indicates nothing more than that the client wants to sync the
terminal with the server.

### Terminal Sync Response
If the client sends a Terminal Sync Request, they get this message back. It
first consists of a checksum of the terminal from the server (8 bytes),
followed by the real-life timestamp (8 bytes) at which the message was send.
The remainder of the message is the entire terminal output. Each message itself
consists out of Terminal Sync Messages, which are defined as a self-sustained
sub-protocol.

### Terminal Message
The Terminal Message is never directly send as a standalone. It is simply
wrapped in a Terminal Public Output Send or a Terminal Sync Response. Its main
goal is to unify the way that public messages are transported. The header of
each such message exists out of a code indicating the message content length
(8 bytes), message error status (1 byte), a real-life timestamp (8 bytes),
an in-simulation timestamp (8 bytes) and the in-simulation origin of the
message (36 bytes). The remainder of the message is the actual terminal
message, in string format.
