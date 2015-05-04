# Format of commands

# Arduino commands #

I've chosen to use a pretty simple format for commands on the Arduino modules:

"[" + command + "]"

The module will look for a "[" and save everything until the next "]" as its command, and then parse it. It can handle multiple commands.

eg: the sequence "`[`l1`]``[`cFF8000`]`" will turn on the light and change the RGB LEDs to orange if sent to the lighting module.

I've chosen to keep my commands plain text to simplify working with them from the browser. It will also make integrating websocket support simpler.


# Server commands #

Commands are sent to the server either via the web interface's form POST or via a TCP socket (telnet).

for POST-ing commands, use the cmd attribute.

The server has a very simple addressing system built in.

examples:
  * "2`[`l0`]`" will send the command "`[`l0`]`" (light off) to the pre-defined module #2.

  * "4`[`t5`]`" will send the command "`[`t5`]`" (timer 5min) to the pre-defined module #4.

  * "`[`ping`]`" will send the command "`[`ping`]`" (unimplemented example) to all devices (broadcast).