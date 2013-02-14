import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("script", help="Python script to invoke")
    parser.add_argument("args", type="...", help="Arguments to the script")
    ns = parser.parse_args()
    print("ns", ns)
