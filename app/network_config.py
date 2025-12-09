"""Network configuration for different Bitcoin networks"""

# Valid networks
VALID_NETWORKS = ['mainchain', 'testnetv3', 'testnetv4', 'signet']

# Mempool service URLs for each network
NETWORK_URLS = {
    'mainchain': 'https://mempool.space/',
    'testnetv3': 'https://mempool.space/testnet/',
    'testnetv4': 'https://mempool.space/testnet4/',
    'signet': 'https://mempool.space/signet/',
}

# Mempool.space explorer URLs for each network
EXPLORER_URLS = {
    'mainchain': 'https://mempool.space/',
    'testnetv3': 'https://mempool.space/testnet/',
    'testnetv4': 'https://mempool.space/testnet4/',
    'signet': 'https://mempool.space/signet/',
}

def get_mempool_url(network):
    """Get mempool service URL for a given network"""
    if network not in VALID_NETWORKS:
        raise ValueError(f"Invalid network: {network}. Valid networks are: {VALID_NETWORKS}")
    return NETWORK_URLS[network]

def get_explorer_url(network):
    """Get mempool.space explorer URL for a given network"""
    if network not in VALID_NETWORKS:
        raise ValueError(f"Invalid network: {network}. Valid networks are: {VALID_NETWORKS}")
    return EXPLORER_URLS[network]

def is_valid_network(network):
    """Check if a network is valid"""
    return network in VALID_NETWORKS

