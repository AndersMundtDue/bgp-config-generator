# configbgp #

*Simple* **BGP** Peering config generator.

It's one thing that this script can actually generate something that parses a
routers syntax checks. It's a whole other story wether or not this might break
your router in really fun ways.

## help page ##

```
Usage: generate.py [options]

Options:
  -h, --help            show this help message and exit
  -T TEMPLATEPATH, --templatepath=TEMPLATEPATH
                        path to search for templates, default to templates
  -t TEMPLATENAME, --templatename=TEMPLATENAME
                        default template, cisco default is cisco.j2, junos
                        default is juniper-set.j2
  -r ROUTER, --router=ROUTER
                        router name to match
  -l, --list            list peers found in json input
  -p PEERS, --peers=PEERS
                        peer match expression
  -i SOURCE, --input=SOURCE
                        json input
  -o OUTPUT, --output=OUTPUT
                        output file
  -c, --cisco           short for -t cisco.j2
  -j, --juniper         short for -t juniper-set.j2
```

### -T / -t ###

Everything works from templates, there's a cisco and two different juniper templates as the moment of writing this,
there may well be more in the future :+1:

 * -T PATH
	* defines a path to search for templates, default to the *templates* directory located together with the generate.py script.

 * -t NAME
	* defines the name of the template to use, default is cisco.j2, unless -j is specified, then juniper-set.j2 is the default.

### -c / -j ###

Basically just shortcuts.

  * -c = -t cisco.j2
  * -j = -t juniper-set.j2

### -l / -r / -p ###

  * -l
	* lists the peers found in the input json file.
  * -p PEERS
	* where PEERS is a fnmatch style expression selecting the peer from the list found with -l
  * -r ROUTER
	* since it's possible to have multiple routers in a json input, this give you the option to only select the routers matching the ROUTER fnmatch expression

### -o / -i ###

  * -o OUTPUT
	* is simply the output file, if the outputfile is '-' then it prints to stdout. defaults to output.cfg

  * -i INPUT
	* is the input json file

### Example[s] ###

Generate peering info using peerings.json, router ly0 and just the service that's service info, also
just send it to stdout for easy copy/paste to the router.

*peerings.json*
```json
{
   "anycastdns": {
      "title" : "dnscahce",
      "asnumber" : 64553,
      "prefixes" : {
         "ipv4" : [ "192.0.2.53/32" ],
         "ipv6" : [ "2001:db8:ac::53/128" ]
      },
      "peerings" : {
         "core1" : { "asnumber": 64512, "ipv4" : "192.0.2.1", "ipv6" : "2001:db8::1" },
         "core2" : { "asnumber": 64512, "ipv4" : "192.0.2.2", "ipv6" : "2001:db8::2" }
      }
   }
}
```

*Output*
```
$ ./generate.py -r core1 -c -p '*anycast*' -o - 
Generating from peerings.json to - using cisco.j2 as template
!
! begin for dnscahce
!
ip prefix-list as64553-prefix permit 192.0.2.53/32
ip prefix-list as64553-prefix deny 0.0.0.0/0 le 32

ipv6 prefix-list as64553-prefix permit 2001:db8:ac::53/128
ipv6 prefix-list as64553-prefix deny ::/0 le 128

route-map as64553-in permit 10
  match ip address prefix-list as64553-prefix
  match ipv6 address prefix-list as64553-prefix

route-map as64553-in deny 100


! begin core1
router bgp 64512
 neighbor 192.0.2.1 remote-as 64553
 neighbor 192.0.2.1 version 4
 neighbor 192.0.2.1 timers 5 20
 neighbor 192.0.2.1 description dnscahce
 address-family ipv4
  no neighbor 2001:DB8::1 activate
  neighbor 192.0.2.1 activate
  neighbor 192.0.2.1 default-originate
  neighbor 192.0.2.1 soft-reconfiguration inbound
  neighbor 192.0.2.1 route-map as64553-in in
  neighbor 192.0.2.1 route-map defaultonly out
 exit-address-family
 address-family ipv6
  neighbor 2001:DB8::1 activate
  neighbor 2001:DB8::1 default-originate
  neighbor 2001:DB8::1 soft-reconfiguration inbound
  neighbor 2001:DB8::1 route-map as64553-in in
  neighbor 2001:DB8::1 route-map defaultonly out
 exit-address-family

! end core1

!
! end for dnscahce
!
```
