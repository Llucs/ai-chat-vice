import yaml

try:
    with open('/home/ubuntu/ai-chat-vice/.github/workflows/deploy-frontend.yml', 'r') as f:
        yaml.safe_load(f)
    print('YAML is valid.')
except yaml.YAMLError as e:
    print(f'YAML error: {e}')
except FileNotFoundError:
    print('File not found.')

