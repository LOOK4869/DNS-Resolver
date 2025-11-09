#!/usr/bin/env python3
import socket
import sys
from dns_resolver import DNSResolver

def main():
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 53
    
    print(f"Starting DNS resolver on port {port}")
    
    resolver = DNSResolver()
    resolver.start(port)

if __name__ == "__main__":
    main()