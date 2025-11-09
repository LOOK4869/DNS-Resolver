# DNS Resolver - Test Commands

## Start DNS Resolver
```bash
python main.py 5354
```
## Test DNS Queries
```bash
dig @127.0.0.1 -p 5354 example.com
dig @127.0.0.1 -p 5354 google.com
dig @127.0.0.1 -p 5354 facebook.com
```
## Batch Test
```bash
for domain in example.com google.com facebook.com; do
    dig @127.0.0.1 -p 5354 $domain +short
done
```
## Expected Output
- Server logs showing iterative resolution
- dig responses with ANSWER SECTION containing correct IP addresses
- Status: NOERROR, flags: qr rd ra
