import yaml


def load_invoice_rules(path):
    with open(path) as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def load_tax_table(text):
    return yaml.load(text, Loader=yaml.FullLoader)
