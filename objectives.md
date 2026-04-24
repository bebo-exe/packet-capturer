## extra objectives of packet analyzer platform

- platform works for both windows and linux
- have a gui interface to show the captured packets in real time
- have a filter system to filter the captured packets by protocol, source, destination, etc
- have a statistics page to show the number of captured packets, the most common protocols, the most common source and destination, etc
- improved code structure and organization such that it is able to perform more like a real packet analyzer platform and be more efficient in capturing and analyzing packets (E.X wireshark)
- include udp, arp, icmp and http/s in the gui interface
- have details when the packet gets captured (its number, source, destination, info)
- an option to save the captured packets in a pcap file
- these saved pcap files are saved in a directory called "capturs"
- and option to load a pcap file and analyze it in the platform
- and option to clear the captured packets from the platform
- a pie chart to show the distribution of the captured packets by protocol, source, destination, etc in real time
- this pie chart should be updated in real time as the packets are captured and analyzed, and it should also have the option to show the distribution of the captured packets by different criteria (protocol, source, destination, etc) and it should also have the option to show the distribution of the captured packets in a specific time range (last 5 minutes, last 10 minutes, etc) and it should also have the option to show the distribution of the captured packets in a specific time range for a specific protocol, source or destination (last 5 minutes for tcp packets, last 10 minutes for packets from a specific source, etc)
- an option to save the statistics of the captured packets in a file that can be loaded later to show the statistics again
- a ruleset system that works this way (an example of the ruleset):
* this system has its own captureing process that is separate from the main capturing process
* the user can start this process at any time and stop it at any time, and in case the user wanted to stop, the number of captured packets should be resaonable in such way that the algorithms can be compared in a good way, so the user can choose to stop the process at any time after it captures 1000 packets at minimum
* if the user wanted to stop the process before it captures 1000 packets, it will show a warning message that says "the capture process should capture at least 1000 packets to be able to compare the algorithms in a good way, do you want to continue?" and if the user chooses to continue, it will stop the process and show the results of the algorithms based on the captured packets, but if the user chooses to cancel, it will continue capturing packets until it reaches 1000 packets at minimum
* the capture process captures 1000 packets at minimum
* while capturing it chooses one packet at random to be set as a ruleset for the rest of the capture process
* this ruleset is then applied as a filter for the packets that are the same as the chosen one
* there are three algorithms to compare them (quick search, boyer moore, aho corasick)
* then comparing each algorithm, their diffrences and their expected time to find the ruleset and how long it took them to find the ruleset in the captured packets
* the user can choose to apply the ruleset as a filter for the captured packets, and then it will show only the packets that match the ruleset
* the user can choose to clear the ruleset and stop applying it as a filter for the captured packets, and then it will show all the captured packets again
* the user can choose to save the ruleset for later use, and then it will be saved in a file that can be loaded later to apply it as a filter for the captured packets
