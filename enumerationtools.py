from flask import Flask, request, jsonify
import dns.resolver
import threading
from queue import Queue

app = Flask(__name__)

def resolve_subdomains(domain, wordlist, result_queue):
    resolver = dns.resolver.Resolver()
    subdomains = []

    with open(wordlist, 'r') as f:
        for line in f:
            subdomain = line.strip()
            try:
                result = resolver.resolve(subdomain + '.' + domain, 'A')
                subdomains.append({
                    'subdomain': subdomain,
                    'ip': [str(record) for record in result]
                })
            except dns.resolver.NXDOMAIN:
                pass
            except dns.resolver.Timeout:
                pass
            except dns.resolver.NoNameservers:
                pass
            except dns.exception.DNSException as e:
                pass

    # Mengirim hasil resolusi subdomain ke dalam antrian
    result_queue.put(subdomains)

def resolve_subdomains_threaded(domain, wordlist):
    # Membuat antrian untuk berbagi hasil antara thread
    result_queue = Queue()

    # Membuat thread untuk menjalankan fungsi resolve_subdomains
    thread = threading.Thread(target=resolve_subdomains, args=(domain, wordlist, result_queue))
    thread.start()
    thread.join()  # Menunggu sampai thread selesai

    # Mengambil hasil dari antrian
    subdomains_result = result_queue.get()

    return subdomains_result

@app.route('/')
def index():
    return "Reconnaissance Tool"

@app.route('/reconnaissance', methods=['POST'])
def reconnaissance():
    data = request.get_json()

    if not data or 'domain' not in data:
        return jsonify({'error': 'Domain not provided'})

    domain = data['domain']

    main_domain_result = resolve_domain(domain)
    
    # Menjalankan fungsi resolve_subdomains_threaded() pada thread terpisah
    subdomains_result = resolve_subdomains_threaded(domain, 'wordlist.txt')

    subdomains_with_urls = []
    for subdomain_info in subdomains_result:
        subdomain = subdomain_info["subdomain"]
        full_url = f"{subdomain}.{domain}"
        subdomains_with_urls.append({
            "subdomain": subdomain,
            "url": full_url,
            "ip": subdomain_info["ip"]
        })

    result = {
        'domain': domain,
        'Main Domain': main_domain_result,
        'Subdomains': subdomains_with_urls
    }

    return jsonify(result)

def resolve_domain(domain):
    resolver = dns.resolver.Resolver()
    result = {}

    try:
        a_records = resolver.resolve(domain, 'A')
        result['A Records'] = [str(record) for record in a_records]
    except dns.resolver.NXDOMAIN:
        pass
    except dns.resolver.Timeout:
        pass
    except dns.resolver.NoNameservers:
        pass
    except dns.exception.DNSException as e:
        pass

    try:
        mx_records = resolver.resolve(domain, 'MX')
        result['MX Records'] = [str(record.exchange) for record in mx_records]
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.Timeout:
        pass
    except dns.resolver.NoNameservers:
        pass
    except dns.exception.DNSException as e:
        pass

    try:
        ns_records = resolver.resolve(domain, 'NS')
        result['NS Records'] = [str(record) for record in ns_records]
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.Timeout:
        pass
    except dns.resolver.NoNameservers:
        pass
    except dns.exception.DNSException as e:
        pass

    try:
        txt_records = resolver.resolve(domain, 'TXT')
        result['TXT Records'] = [str(record) for record in txt_records]
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.Timeout:
        pass
    except dns.resolver.NoNameservers:
        pass
    except dns.exception.DNSException as e:
        pass

    return result
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000, debug=True)
